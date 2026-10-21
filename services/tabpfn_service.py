import os
import re
import logging
from typing import Union, List, Dict, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

import config

logger = logging.getLogger("sloth_tabpfn")
logging.basicConfig(level=logging.INFO)

FEATURE_COLUMNS = [
    "num_ingredients",
    "requires_knife",
    "heat_source",
    "has_dairy_curd",
    "has_eggs_protein",
    "has_bread_grain",
    "sloth_level"
]
CATEGORICAL_TARGET = "fatigue_tier"
REGRESSION_TARGET = "active_standing_mins"


class TabPFNSlothEngine:
    """
    TabPFN-powered engine to predict cooking fatigue, standing time,
    and utensil penalties for couch-bound cooks.
    """

    def __init__(self, data_path: str = "data/sloth_meals.csv"):
        self.data_path = data_path
        self.clf = None
        self.reg = None
        self.is_tabpfn_active = False

        # Fallback scikit-learn models (trained on identical reference dataset)
        self.fallback_clf = None
        self.fallback_reg = None

        self._load_and_train()

    def _load_and_train(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Reference dataset not found at {self.data_path}")

        df = pd.read_csv(self.data_path)
        X = df[FEATURE_COLUMNS].values
        y_class = df[CATEGORICAL_TARGET].values
        y_reg = df[REGRESSION_TARGET].values

        # 1. Train Fallback models first to guarantee 100% operational readiness
        try:
            self.fallback_clf = RandomForestClassifier(n_estimators=60, random_state=42)
            self.fallback_clf.fit(X, y_class)

            self.fallback_reg = RandomForestRegressor(n_estimators=60, random_state=42)
            self.fallback_reg.fit(X, y_reg)
            logger.info("Initialized high-accuracy fallback ML models on sloth_meals.csv.")
        except Exception as e:
            logger.error(f"Error training fallback models: {e}")

        # 2. Attempt TabPFN Initialization
        if config.TABPFN_TOKEN:
            os.environ["TABPFN_TOKEN"] = config.TABPFN_TOKEN

        try:
            from tabpfn import TabPFNClassifier, TabPFNRegressor

            logger.info("Attempting TabPFN initialization...")
            clf = TabPFNClassifier(device="cpu")
            clf.fit(X, y_class)

            # Fit regressor if supported
            reg = None
            try:
                reg = TabPFNRegressor(device="cpu")
                reg.fit(X, y_reg)
            except Exception as reg_err:
                logger.warning(f"TabPFNRegressor initialization warning: {reg_err}. Using regression fallback.")

            self.clf = clf
            self.reg = reg
            self.is_tabpfn_active = True
            logger.info("TabPFNClassifier and Regressor successfully loaded and fitted!")
        except Exception as ex:
            logger.warning(
                f"TabPFN requires TABPFN_TOKEN or interactive license check ({ex}). "
                "Operating in zero-latency fallback engine mode."
            )
            self.is_tabpfn_active = False

    def parse_ingredients(self, ingredients_input: Union[str, List[str]], sloth_level: int) -> Dict[str, int]:
        """
        Parses raw ingredients string or array into feature flags.
        """
        if isinstance(ingredients_input, list):
            raw_text = " ".join(ingredients_input).lower()
            num_ingredients = max(1, min(8, len(ingredients_input)))
        else:
            raw_text = str(ingredients_input).lower()
            # Split by comma or newline
            items = [item.strip() for item in re.split(r"[,;\n]+", raw_text) if item.strip()]
            num_ingredients = max(1, min(8, len(items)))

        # Keywords for dairy / curd
        dairy_patterns = [r"\bcurd\b", r"\bdahi\b", r"\bcheese\b", r"\bpaneer\b", r"\bmilk\b",
                          r"\byogurt\b", r"\bbutter\b", r"\bcream\b", r"\bghee\b"]
        has_dairy = 1 if any(re.search(p, raw_text) for p in dairy_patterns) else 0

        # Keywords for eggs / protein
        egg_patterns = [r"\begg\b", r"\beggs\b", r"\banda\b", r"\bchicken\b", r"\bprotein\b",
                        r"\btofu\b", r"\bsoya\b", r"\bmeat\b", r"\bham\b", r"\bsausage\b", r"\bbacon\b", r"\btuna\b"]
        has_eggs = 1 if any(re.search(p, raw_text) for p in egg_patterns) else 0

        # Keywords for bread / grains / carbs
        bread_patterns = [r"\bbread\b", r"\btoast\b", r"\broti\b", r"\brice\b", r"\boats\b",
                          r"\bmaggi\b", r"\bnoodles\b", r"\bpasta\b", r"\bbun\b", r"\btortilla\b", r"\bwrap\b"]
        has_bread = 1 if any(re.search(p, raw_text) for p in bread_patterns) else 0

        # Knife requirement logic
        # If sloth_level == 3 (couch potato comatose), no knife is permitted
        if sloth_level == 3:
            requires_knife = 0
        else:
            knife_cues = [r"\bchop\b", r"\bcut\b", r"\bdice\b", r"\bslice\b", r"\bonion\b",
                          r"\bpotato\b", r"\bcarrot\b", r"\bcapsicum\b", r"\bvegetable\b", r"\bveggies\b"]
            if any(re.search(p, raw_text) for p in knife_cues) or num_ingredients >= 5:
                requires_knife = 1
            else:
                requires_knife = 0

        return {
            "num_ingredients": num_ingredients,
            "requires_knife": requires_knife,
            "has_dairy_curd": has_dairy,
            "has_eggs_protein": has_eggs,
            "has_bread_grain": has_bread
        }

    def evaluate_sloth_fatigue(
        self,
        ingredients_list: Union[str, List[str]],
        heat_source_str: str = "skillet",
        sloth_level: int = 2
    ) -> Dict[str, Any]:
        """
        Calculates fatigue tier, predicted standing time, sink dish penalty,
        posterior probabilities, and sloth approval score.
        """
        # Map heat source: "microwave" -> 0, "skillet" -> 1, "stove" / "oven" -> 2
        hs_clean = heat_source_str.strip().lower()
        if "micro" in hs_clean or "mug" in hs_clean:
            heat_source = 0
        elif "skillet" in hs_clean or "pan" in hs_clean:
            heat_source = 1
        elif "oven" in hs_clean or "stove" in hs_clean or "pot" in hs_clean:
            heat_source = 2
        else:
            heat_source = 1

        sloth_level = max(1, min(3, int(sloth_level)))

        # Feature parsing
        parsed = self.parse_ingredients(ingredients_list, sloth_level)
        X_vec = np.array([[
            parsed["num_ingredients"],
            parsed["requires_knife"],
            heat_source,
            parsed["has_dairy_curd"],
            parsed["has_eggs_protein"],
            parsed["has_bread_grain"],
            sloth_level
        ]])

        # 1. Classification & Class Probabilities
        if self.is_tabpfn_active and self.clf is not None:
            try:
                preds = self.clf.predict(X_vec)
                predicted_tier = str(preds[0])
                probas = self.clf.predict_proba(X_vec)[0]
                classes = self.clf.classes_
                class_probabilities = {str(c): round(float(p), 4) for c, p in zip(classes, probas)}
            except Exception as e:
                logger.warning(f"TabPFNClassifier inference error: {e}. Using fallback.")
                predicted_tier = None
        else:
            predicted_tier = None

        if predicted_tier is None:
            preds = self.fallback_clf.predict(X_vec)
            predicted_tier = str(preds[0])
            probas = self.fallback_clf.predict_proba(X_vec)[0]
            classes = self.fallback_clf.classes_
            class_probabilities = {str(c): round(float(p), 4) for c, p in zip(classes, probas)}

        # Strict domain rule enforcement:
        # sloth_level=3 or heat_source=0 -> fatigue_tier="Zero Effort (Mug)"
        if sloth_level == 3 or heat_source == 0:
            predicted_tier = "Zero Effort (Mug)"
            # Adjust probabilities slightly to reflect domain certainty
            class_probabilities = {
                "Zero Effort (Mug)": max(class_probabilities.get("Zero Effort (Mug)", 0.8), 0.88),
                "Low Effort (1 Pan)": min(class_probabilities.get("Low Effort (1 Pan)", 0.1), 0.10),
                "High Effort (Avoid)": min(class_probabilities.get("High Effort (Avoid)", 0.02), 0.02)
            }
            # Normalize
            total_p = sum(class_probabilities.values())
            class_probabilities = {k: round(v / total_p, 4) for k, v in class_probabilities.items()}

        # 2. Continuous Regression (active standing minutes)
        if self.is_tabpfn_active and self.reg is not None:
            try:
                reg_pred = self.reg.predict(X_vec)[0]
                standing_time = float(reg_pred)
            except Exception:
                standing_time = None
        else:
            standing_time = None

        if standing_time is None:
            if self.fallback_reg is not None:
                standing_time = float(self.fallback_reg.predict(X_vec)[0])
            else:
                # Rule-based fallback
                if predicted_tier == "Zero Effort (Mug)":
                    standing_time = 2.8
                elif predicted_tier == "Low Effort (1 Pan)":
                    standing_time = 6.2
                else:
                    standing_time = 14.5

        # Bound standing time based on predicted tier
        if predicted_tier == "Zero Effort (Mug)":
            standing_time = max(2.0, min(4.0, standing_time))
        elif predicted_tier == "Low Effort (1 Pan)":
            standing_time = max(4.5, min(8.0, standing_time))
        else:
            standing_time = max(11.5, min(18.0, standing_time))

        standing_time = round(float(standing_time), 1)

        # 3. Sink Dishes Penalty:
        # "Zero Effort (Mug)": 1 utensil (mug/fork, eat directly)
        # "Low Effort (1 Pan)": 2 utensils (skillet + spatula, eat directly from pan)
        # "High Effort (Avoid)": 4 utensils
        if predicted_tier == "Zero Effort (Mug)":
            sink_dishes_count = 1
        elif predicted_tier == "Low Effort (1 Pan)":
            sink_dishes_count = 2
        else:
            sink_dishes_count = 4

        # 4. Sloth Approval Score: 0 to 100 (higher = lazier)
        # Inversely proportional to standing time and dish count
        if predicted_tier == "Zero Effort (Mug)":
            # 90 to 99
            base_score = 100 - (standing_time * 2.0) - (sink_dishes_count * 2.0)
            sloth_approval_score = max(88, min(99, int(round(base_score))))
        elif predicted_tier == "Low Effort (1 Pan)":
            # 65 to 85
            base_score = 92 - (standing_time * 2.8) - (sink_dishes_count * 3.0)
            sloth_approval_score = max(60, min(85, int(round(base_score))))
        else:
            # 10 to 45
            base_score = 65 - (standing_time * 2.0) - (sink_dishes_count * 5.0)
            sloth_approval_score = max(10, min(45, int(round(base_score))))

        return {
            "fatigue_tier": predicted_tier,
            "standing_time_mins": standing_time,
            "sink_dishes_count": sink_dishes_count,
            "class_probabilities": class_probabilities,
            "sloth_approval_score": sloth_approval_score
        }


# Global singleton instance
tabpfn_engine = TabPFNSlothEngine()


def evaluate_sloth_fatigue(ingredients_list: Union[str, List[str]], heat_source_str: str = "skillet", sloth_level: int = 2) -> Dict[str, Any]:
    """Module-level helper matching Step 3 signature."""
    return tabpfn_engine.evaluate_sloth_fatigue(ingredients_list, heat_source_str, sloth_level)
