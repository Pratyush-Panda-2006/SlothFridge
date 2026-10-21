import json
import logging
from typing import Dict, Any
from groq import Groq

import config

logger = logging.getLogger("sloth_gemma")
logging.basicConfig(level=logging.INFO)

# Initialize Groq client if key is available
groq_client = None
if config.GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=config.GROQ_API_KEY)
        logger.info("Groq client initialized successfully.")
    except Exception as e:
        logger.warning(f"Failed to initialize Groq client: {e}")
else:
    logger.info("GROQ_API_KEY not found. Fallback lazy recipes will be utilized until configured.")


def _generate_fallback_recipe(ingredients: str, fatigue_info: dict, sloth_level: int) -> dict:
    """
    Guaranteed witty, valid fallback recipe adhering to sloth constraints
    if the Groq API key is missing or encounters a rate-limit/network error.
    """
    tier = fatigue_info.get("fatigue_tier", "Low Effort (1 Pan)")
    standing = fatigue_info.get("standing_time_mins", 5.0)
    dishes = fatigue_info.get("sink_dishes_count", 2)
    ing_lower = str(ingredients).lower()

    if "Zero Effort" in tier or sloth_level == 3:
        recipe_name = "Microwave Curd & Cheese Mug-Drop"
        prep_effort_tagline = f"Requires zero vertical posture. Ready in {standing} minutes with only 1 mug to wash."
        lazy_rules = [
            "Do not cut anything with a knife; use your thumbs or gravity.",
            "Eat directly out of the mug with a single spoon or fork.",
            "If you spill a speck on the counter, leave it for your future self."
        ]
        steps = [
            f"Fling whatever you have ({ingredients}) directly into a large microwave-safe ceramic mug.",
            "Stir once with minimal forearm rotation, then microwave on HIGH for 90 seconds while leaning against the counter.",
            "Remove mug with a towel if hot, drag your feet back to bed, and eat directly from the vessel."
        ]
        sleepy_audio_script = (
            "Listen to me closely. Do not stand up straight. Just throw the ingredients in a mug and hit ninety seconds on the microwave. "
            "Lie completely flat on your mattress until you hear the beep. Eat it straight from the mug so you do not have to look at the sink."
        )
    elif "High Effort" in tier:
        recipe_name = "The Couch Potato Triage Skillet"
        prep_effort_tagline = f"Demoted from a complex meal down to an unapologetic {standing}-minute pan dump."
        lazy_rules = [
            "Tear and crush ingredients with hands; do not dirty a cutting board.",
            "Under no circumstances should you wash a plate; eat straight from the pan after it cools.",
            "If something requires peeling, either eat the peel or discard the item entirely."
        ]
        steps = [
            f"Toss {ingredients} aggressively into a cold skillet with a splash of oil or butter.",
            f"Turn the burner to medium-low and shuffle back to the sofa for {int(standing - 2)} minutes.",
            "Give it one half-hearted fold with a spatula, turn off the flame, and pull the skillet onto a heat mat next to your bed."
        ]
        sleepy_audio_script = (
            "You were thinking about cooking an actual meal, but we both know you are too tired for that. "
            "Dump everything into the pan, turn the flame on low, and walk right back to your sofa. "
            "Return only when you smell hot food, and eat it straight from the metal."
        )
    else:  # Low Effort (1 Pan)
        recipe_name = "The 1-Skillet Bread-Egg Slump"
        prep_effort_tagline = f"Maximum caloric reward for {standing} minutes of standing and only {dishes} items to wash."
        lazy_rules = [
            "Tear the bread into random ragged pieces with your fingers.",
            "Crack eggs directly into the hot pan over the bread; no whisking bowl permitted.",
            "Eat straight out of the skillet using the spatula as a makeshift shovel."
        ]
        steps = [
            f"Melt a knob of butter or oil in the pan, then hand-tear {ingredients} into uneven chunks right over the heat.",
            f"Crack in the eggs, crumble cheese or curd over top, and stand idle for {int(standing)} minutes without overthinking.",
            "Slide skillet off the heat onto a coaster in bed, and enjoy zero cleanup."
        ]
        sleepy_audio_script = (
            "Tear the bread with your bare hands and drop it in the pan. Crack the eggs right on top and let heat do the work. "
            "Go lie down flat on your bed for five minutes. Come back when it crackles, and eat straight from the skillet."
        )

    return {
        "recipe_name": recipe_name,
        "prep_effort_tagline": prep_effort_tagline,
        "lazy_rules": lazy_rules,
        "steps": steps,
        "sleepy_audio_script": sleepy_audio_script
    }


def synthesize_sloth_recipe(ingredients: str, fatigue_info: dict, sloth_level: int = 2) -> dict:
    """
    Synthesizes an ultra-lazy, couch-potato recipe via Gemma 2 on Groq,
    with an ironclad fallback if unauthenticated or rate-limited.
    """
    tier = fatigue_info.get("fatigue_tier", "Low Effort (1 Pan)")
    standing_time = fatigue_info.get("standing_time_mins", 6.0)
    sink_dishes = fatigue_info.get("sink_dishes_count", 2)

    # Use fallback if client is not configured
    if not groq_client:
        return _generate_fallback_recipe(ingredients, fatigue_info, sloth_level)

    system_prompt = (
        f"You are an unapologetically lazy, world-weary chef speaking to someone lying completely flat on their bed or sofa.\n"
        f"Available ingredients: {ingredients}.\n"
        f"Target fatigue tier: {tier}.\n"
        f"Standing limit: {standing_time} minutes.\n"
        f"Utensil limit: {sink_dishes} dishes max.\n\n"
        "Rules:\n"
        "Zero complex prep. No fine chopping, dicing, or julienning. Tell them to tear bread with hands, crack eggs straight in, or crush onions with a cup.\n"
        "Recommend eating straight out of the pan or mug so they don't have to wash a plate.\n"
        "Keep steps to 3 or 4 minimal-effort sentences.\n\n"
        "Return strict JSON matching this exact structure:\n"
        "{\n"
        "  \"recipe_name\": \"A funny, low-effort recipe title (e.g., The 1-Skillet Bread-Egg Slump or Microwave Curd Mug-Drop)\",\n"
        "  \"prep_effort_tagline\": \"Short summary of why this takes zero energy\",\n"
        "  \"lazy_rules\": [\n"
        "    \"Rule 1 (e.g. Do not cut with a knife; tear with hands)\",\n"
        "    \"Rule 2 (e.g. Eat directly from the pan to spare the sink)\"\n"
        "  ],\n"
        "  \"steps\": [\n"
        "    \"Step 1...\",\n"
        "    \"Step 2...\",\n"
        "    \"Step 3...\"\n"
        "  ],\n"
        "  \"sleepy_audio_script\": \"A 3-sentence slow, deadpan monologue for the cook instructing them to dump everything in, set heat to low, lie back down on the bed, and return when it smells ready.\"\n"
        "}"
    )

    user_prompt = (
        f"Cook something with: {ingredients}. "
        f"Sloth level: {sloth_level}/3. Make it ridiculously low effort."
    )

    try:
        completion = groq_client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        content = completion.choices[0].message.content
        data = json.loads(content)

        # Validate required keys
        required_keys = ["recipe_name", "prep_effort_tagline", "lazy_rules", "steps", "sleepy_audio_script"]
        if all(k in data for k in required_keys):
            return data
        else:
            logger.warning(f"Groq response missing required keys: {data.keys()}. Merging with fallback.")
            fb = _generate_fallback_recipe(ingredients, fatigue_info, sloth_level)
            fb.update({k: data[k] for k in required_keys if k in data})
            return fb

    except Exception as e:
        logger.error(f"Error calling Groq gemma2-9b-it: {e}. Falling back to offline generator.")
        return _generate_fallback_recipe(ingredients, fatigue_info, sloth_level)
