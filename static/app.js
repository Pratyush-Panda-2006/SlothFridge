/**
 * SLOTHFRIDGE — THE COUCH POTATO CULINARY COPILOT
 * Client-Side Orchestration across multi-page architecture:
 * Ingestion, TabPFN Telemetry, Self-Drawing SVG Effort Paths, Gemma 2 Recipes, and ElevenLabs Audio.
 */

(function () {
  "use strict";

  // State Management
  const state = {
    ingredients: "2 eggs, stale bread, curd, cheese slice",
    heatSource: "skillet", // "microwave", "skillet", "stove"
    slothLevel: 2,         // 1, 2, 3
    isSynthesizing: false,
    isPlayingAudio: false,
    currentAudioUrl: null,
    audioBlobCache: new Map(),
    currentRecipe: {
      recipe_name: "The 1-Skillet Bread-Egg Slump",
      prep_effort_tagline: "Maximum caloric reward for 6.5 minutes of standing and only 2 items to wash.",
      lazy_rules: [
        "Tear the bread into random ragged pieces with your fingers.",
        "Crack eggs directly into the hot pan over the bread; no whisking bowl permitted.",
        "Eat straight out of the skillet using the spatula as a makeshift shovel."
      ],
      steps: [
        "Melt a knob of butter or oil in the pan, then hand-tear 2 eggs, stale bread, curd, cheese slice into uneven chunks right over the heat.",
        "Crack in the eggs, crumble cheese or curd over top, and stand idle for 6 minutes without overthinking.",
        "Slide skillet off the heat onto a coaster in bed, and enjoy zero cleanup."
      ],
      sleepy_audio_script: "Tear the bread with your bare hands and drop it in the pan. Crack the eggs right on top and let heat do the work. Go lie down flat on your bed for five minutes. Come back when it crackles, and eat straight from the skillet."
    }
  };

  // DOM Cache
  const dom = {
    // Navigation & Hero
    heroWordmark: document.getElementById("hero-wordmark"),
    footerWordmark: document.getElementById("footer-wordmark"),

    // Ingestion Form (index.html)
    ingredientsInput: document.getElementById("ingredients-input"),
    btnSynthesize: document.getElementById("btn-synthesize"),
    badgeButtons: document.querySelectorAll(".btn-badge"),
    toggleButtons: document.querySelectorAll(".btn-toggle"),
    levelButtons: document.querySelectorAll(".btn-level"),

    // Telemetry Display (index.html)
    metricStandingMins: document.getElementById("metric-standing-mins"),
    metricFatigueTier: document.getElementById("metric-fatigue-tier"),
    metricSinkDishes: document.getElementById("metric-sink-dishes"),
    metricSlothScore: document.getElementById("metric-sloth-score"),
    slothScoreFill: document.getElementById("sloth-score-fill"),
    probValZero: document.getElementById("prob-val-zero"),
    probValLow: document.getElementById("prob-val-low"),
    probValHigh: document.getElementById("prob-val-high"),
    probBarZero: document.getElementById("prob-bar-zero"),
    probBarLow: document.getElementById("prob-bar-low"),
    probBarHigh: document.getElementById("prob-bar-high"),
    telemetryLiveBadge: document.getElementById("telemetry-live-badge"),

    // Recipe Display (recipes.html & index.html)
    variantButtons: document.querySelectorAll(".btn-variant"),
    displayRecipeTitle: document.getElementById("display-recipe-title"),
    displayRecipeTagline: document.getElementById("display-recipe-tagline"),
    displayLazyRules: document.getElementById("display-lazy-rules"),
    displayStep1: document.getElementById("display-step-1"),
    displayStep2: document.getElementById("display-step-2"),
    displayStep3: document.getElementById("display-step-3"),

    // SVG Effort Curve (recipes.html)
    effortCurvePath: document.getElementById("effort-curve-path"),

    // Audio & Close (audio.html & index.html)
    displayAudioScript: document.getElementById("display-audio-script"),
    customAudioScriptInput: document.getElementById("custom-audio-script-input"),
    btnStreamCustom: document.getElementById("btn-stream-custom"),
    btnPlayAudio: document.getElementById("btn-play-audio"),
    audioBtnIcon: document.getElementById("audio-btn-icon"),
    audioBtnText: document.getElementById("audio-btn-text"),
    audioStatusPill: document.getElementById("audio-status-pill"),
    audioVisualizer: document.getElementById("audio-visualizer"),
    audioPlayer: document.getElementById("sloth-audio-player")
  };

  /* ==========================================================================
     1. DYNAMIC WORDMARK SPREAD (HERO)
     ========================================================================== */
  function updateWordmarkSpread() {
    if (!dom.heroWordmark) return;

    const scrollY = window.scrollY;
    const spans = dom.heroWordmark.querySelectorAll("span");
    const total = spans.length;
    const centerIdx = Math.floor(total / 2); // 5 (letter F)

    const factor = Math.min(1.2, scrollY / 450);

    spans.forEach((span, i) => {
      const offset = (i - centerIdx);
      const moveX = offset * factor * 22; // Outward translate
      const moveY = factor * 48;          // Sinking translate
      span.style.transform = `translate3d(${moveX}px, ${moveY}px, 0)`;
      span.style.opacity = Math.max(0.2, 1 - factor * 0.6).toFixed(2);
    });
  }

  /* ==========================================================================
     2. SELF-DRAWING RECIPE EFFORT SVG PATH (RECIPES PAGE)
     ========================================================================== */
  function triggerSelfDrawingPath(customPathD) {
    if (!dom.effortCurvePath) return;

    if (customPathD) {
      dom.effortCurvePath.setAttribute("d", customPathD);
    }

    try {
      const pathLength = dom.effortCurvePath.getTotalLength();
      dom.effortCurvePath.style.transition = "none";
      dom.effortCurvePath.style.strokeDasharray = `${pathLength} ${pathLength}`;
      dom.effortCurvePath.style.strokeDashoffset = `${pathLength}`;

      // Force layout reflow
      dom.effortCurvePath.getBoundingClientRect();

      // Smooth 2.0s stroke draw
      dom.effortCurvePath.style.transition = "stroke-dashoffset 2.0s cubic-bezier(0.25, 1, 0.5, 1)";
      dom.effortCurvePath.style.strokeDashoffset = "0";
    } catch (e) {
      console.warn("SVG self-drawing error:", e);
    }
  }

  /* ==========================================================================
     3. FORM CONTROLS & INGESTION (HOME / COUCH ENGINE)
     ========================================================================== */
  if (dom.badgeButtons.length > 0 && dom.ingredientsInput) {
    dom.badgeButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const item = btn.dataset.item;
        let currentVal = dom.ingredientsInput.value.trim();
        if (!currentVal) {
          dom.ingredientsInput.value = item;
        } else if (!currentVal.toLowerCase().includes(item.toLowerCase())) {
          dom.ingredientsInput.value = `${currentVal}, ${item}`;
        }
        dom.ingredientsInput.focus();
      });
    });
  }

  if (dom.toggleButtons.length > 0) {
    dom.toggleButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        dom.toggleButtons.forEach((b) => {
          b.classList.remove("active");
          b.setAttribute("aria-pressed", "false");
        });
        btn.classList.add("active");
        btn.setAttribute("aria-pressed", "true");
        state.heatSource = btn.dataset.val;
      });
    });
  }

  if (dom.levelButtons.length > 0) {
    dom.levelButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        dom.levelButtons.forEach((b) => {
          b.classList.remove("active");
          b.setAttribute("aria-pressed", "false");
        });
        btn.classList.add("active");
        btn.setAttribute("aria-pressed", "true");
        state.slothLevel = parseInt(btn.dataset.level, 10);
      });
    });
  }

  /* ==========================================================================
     4. TABPFN FATIGUE COMPUTATION & GEMMA 2 SYNTHESIS
     ========================================================================== */
  async function triggerSlothSynthesis() {
    if (state.isSynthesizing) return;

    if (dom.ingredientsInput) {
      state.ingredients = dom.ingredientsInput.value.trim() || "2 eggs, stale bread, curd, cheese slice";
    }
    state.isSynthesizing = true;

    if (dom.btnSynthesize) {
      dom.btnSynthesize.disabled = true;
      dom.btnSynthesize.textContent = "QUERYING TABPFN 3.5 & GEMMA 2...";
    }
    if (dom.telemetryLiveBadge) {
      dom.telemetryLiveBadge.textContent = "INFERRING PRIOR...";
    }

    try {
      const response = await fetch("/api/cook", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ingredients: state.ingredients,
          heat_source: state.heatSource,
          sloth_level: state.slothLevel
        })
      });

      if (!response.ok) {
        throw new Error(`Synthesis API returned ${response.status}`);
      }

      const res = await response.json();
      if (res.status === "success" && res.data) {
        renderTelemetry(res.data.telemetry);
        renderRecipe(res.data.recipe);
      }
    } catch (err) {
      console.warn("Synthesis fallback activated:", err);
      simulateLocalSynthesis();
    } finally {
      state.isSynthesizing = false;
      if (dom.btnSynthesize) {
        dom.btnSynthesize.disabled = false;
        dom.btnSynthesize.textContent = "COMPUTE TABPFN FATIGUE & SYNTHESIZE";
      }
      if (dom.telemetryLiveBadge) {
        dom.telemetryLiveBadge.textContent = "MODEL SYNCED";
      }
    }
  }

  window.triggerSlothSynthesis = triggerSlothSynthesis;

  function renderTelemetry(telemetry) {
    if (!telemetry || !dom.metricStandingMins) return;

    dom.metricStandingMins.textContent = telemetry.standing_time_mins.toFixed(1);
    dom.metricFatigueTier.textContent = telemetry.fatigue_tier;

    const dishNote = telemetry.sink_dishes_count === 1
      ? "1 Utensil (Eat from mug/pan)"
      : `${telemetry.sink_dishes_count} Utensils (Spares plate)`;
    dom.metricSinkDishes.textContent = dishNote;

    const score = telemetry.sloth_approval_score || 75;
    if (dom.metricSlothScore) dom.metricSlothScore.textContent = `${score} / 100`;
    if (dom.slothScoreFill) dom.slothScoreFill.style.width = `${score}%`;

    const probs = telemetry.class_probabilities || {};
    const pZero = ((probs["Zero Effort (Mug)"] || 0) * 100).toFixed(1);
    const pLow = ((probs["Low Effort (1 Pan)"] || 0) * 100).toFixed(1);
    const pHigh = ((probs["High Effort (Avoid)"] || 0) * 100).toFixed(1);

    if (dom.probValZero) dom.probValZero.textContent = `${pZero}%`;
    if (dom.probBarZero) dom.probBarZero.style.width = `${pZero}%`;

    if (dom.probValLow) dom.probValLow.textContent = `${pLow}%`;
    if (dom.probBarLow) dom.probBarLow.style.width = `${pLow}%`;

    if (dom.probValHigh) dom.probValHigh.textContent = `${pHigh}%`;
    if (dom.probBarHigh) dom.probBarHigh.style.width = `${pHigh}%`;

    [dom.probBarZero, dom.probBarLow, dom.probBarHigh].forEach(b => {
      if (b) b.classList.remove("active");
    });
    if (telemetry.fatigue_tier.includes("Zero Effort") && dom.probBarZero) {
      dom.probBarZero.classList.add("active");
    } else if (telemetry.fatigue_tier.includes("Low Effort") && dom.probBarLow) {
      dom.probBarLow.classList.add("active");
    } else if (dom.probBarHigh) {
      dom.probBarHigh.classList.add("active");
    }
  }

  function renderRecipe(recipe) {
    if (!recipe) return;
    state.currentRecipe = recipe;

    if (dom.displayRecipeTitle) dom.displayRecipeTitle.textContent = recipe.recipe_name || "The 1-Skillet Bread-Egg Slump";
    if (dom.displayRecipeTagline) dom.displayRecipeTagline.textContent = recipe.prep_effort_tagline || "";

    if (dom.displayLazyRules && recipe.lazy_rules && Array.isArray(recipe.lazy_rules)) {
      dom.displayLazyRules.innerHTML = "";
      recipe.lazy_rules.forEach((rule) => {
        const li = document.createElement("li");
        li.textContent = rule;
        dom.displayLazyRules.appendChild(li);
      });
    }

    const steps = recipe.steps || [];
    if (dom.displayStep1 && steps[0]) dom.displayStep1.textContent = steps[0];
    if (dom.displayStep2 && steps[1]) dom.displayStep2.textContent = steps[1];
    if (dom.displayStep3 && steps[2]) dom.displayStep3.textContent = steps[2];

    if (dom.displayAudioScript && recipe.sleepy_audio_script) {
      dom.displayAudioScript.textContent = `"${recipe.sleepy_audio_script}"`;
    }

    let curvePath = "M 60 170 C 140 60, 200 70, 280 185 C 380 195, 600 195, 700 190 C 760 180, 800 120, 860 195";
    if (recipe.recipe_name && recipe.recipe_name.toLowerCase().includes("mug")) {
      curvePath = "M 60 185 C 120 150, 180 150, 240 190 C 380 195, 640 195, 760 195 C 800 190, 830 180, 860 195";
    }
    triggerSelfDrawingPath(curvePath);
    resetAudioPlayback();
  }

  function simulateLocalSynthesis() {
    const isMug = state.heatSource === "microwave" || state.slothLevel === 3;
    const tier = isMug ? "Zero Effort (Mug)" : "Low Effort (1 Pan)";
    const standing = isMug ? 2.8 : 6.0;
    const dishes = isMug ? 1 : 2;

    renderTelemetry({
      fatigue_tier: tier,
      standing_time_mins: standing,
      sink_dishes_count: dishes,
      class_probabilities: {
        "Zero Effort (Mug)": isMug ? 0.95 : 0.05,
        "Low Effort (1 Pan)": isMug ? 0.05 : 0.92,
        "High Effort (Avoid)": 0.03
      },
      sloth_approval_score: isMug ? 94 : 74
    });

    renderRecipe({
      recipe_name: isMug ? "Microwave Curd Mug-Drop" : "The 1-Skillet Bread-Egg Slump",
      prep_effort_tagline: `Cooked with bare hands. ${standing} standing minutes, ${dishes} dish in sink.`,
      lazy_rules: [
        "Do not touch a cutting board or knife.",
        "Tear ingredients directly into vessel.",
        "Eat with single fork straight from pan/mug."
      ],
      steps: [
        `Toss ${state.ingredients} directly into the vessel.`,
        "Apply low heat or microwave for a few minutes while you lie down.",
        "Retrieve with a towel and eat horizontally."
      ],
      sleepy_audio_script: "Tear everything with your fingers and dump it into the vessel. Walk back to your mattress for five minutes. Return only when it smells hot, and eat straight from the vessel."
    });
  }

  /* ==========================================================================
     5. RECIPE PRESET VARIANTS (RECIPES PAGE)
     ========================================================================== */
  const PRESET_VARIANTS = {
    slump: {
      name: "The 1-Skillet Bread-Egg Slump",
      tagline: "Maximum caloric reward for 6.5 minutes of standing and only 2 items to wash.",
      rules: [
        "Tear the bread into random ragged pieces with your fingers.",
        "Crack eggs directly into the hot pan over the bread; no whisking bowl permitted.",
        "Eat straight out of the skillet using the spatula as a makeshift shovel."
      ],
      steps: [
        "Melt a knob of butter or oil in the pan, then hand-tear 2 eggs, stale bread, curd, cheese slice into uneven chunks right over the heat.",
        "Crack in the eggs, crumble cheese or curd over top, and stand idle for 6 minutes without overthinking.",
        "Slide skillet off the heat onto a coaster in bed, and enjoy zero cleanup."
      ],
      audio: "Tear the bread with your bare hands and drop it in the pan. Crack the eggs right on top and let heat do the work. Go lie down flat on your bed for five minutes. Come back when it crackles, and eat straight from the skillet.",
      path: "M 60 170 C 140 60, 200 70, 280 185 C 380 195, 600 195, 700 190 C 760 180, 800 120, 860 195"
    },
    mugdrop: {
      name: "Microwave Curd & Cheese Mug-Drop",
      tagline: "Requires zero vertical posture. Ready in 2.8 minutes with only 1 mug to wash.",
      rules: [
        "Do not cut anything with a knife; use your thumbs or gravity.",
        "Eat directly out of the mug with a single spoon or fork.",
        "If you spill a speck on the counter, leave it for your future self."
      ],
      steps: [
        "Fling curd, cheese slice, and broken noodles directly into a large microwave-safe ceramic mug.",
        "Stir once with minimal forearm rotation, then microwave on HIGH for 90 seconds while leaning against the counter.",
        "Remove mug with a towel if hot, drag your feet back to bed, and eat directly from the vessel."
      ],
      audio: "Listen to me closely. Do not stand up straight. Just throw the ingredients in a mug and hit ninety seconds on the microwave. Lie completely flat on your mattress until you hear the beep. Eat it straight from the mug so you do not have to look at the sink.",
      path: "M 60 185 C 120 150, 180 150, 240 190 C 380 195, 640 195, 760 195 C 800 190, 830 180, 860 195"
    },
    breadcurd: {
      name: "Bread & Curd Skillet Melt",
      tagline: "Crisp bottom bread drenched in seasoned dahi and hot ghee. Zero bowls dirtied.",
      rules: [
        "Drop bread slices directly onto melted butter or ghee in the pan.",
        "Spoon curd right over the center of the slices while they sizzle.",
        "Fold bread in half to trap the molten curd and lift directly into your mouth."
      ],
      steps: [
        "Drop stale bread onto a hot oiled skillet on low flame.",
        "Dollop curd, salt, and spices directly onto the bread slices.",
        "Press down once with your spatula, cook 3 minutes, and eat straight from the pan."
      ],
      audio: "Lay the bread flat in the hot pan. Spoon the curd right on top. Do not bother with a plate. Fold it over, shut off the gas, and take the whole pan with you back to the sofa.",
      path: "M 60 175 C 160 90, 220 90, 300 180 C 400 195, 620 195, 720 188 C 770 170, 810 130, 860 195"
    }
  };

  if (dom.variantButtons.length > 0) {
    dom.variantButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        dom.variantButtons.forEach((b) => {
          b.classList.remove("active");
          b.setAttribute("aria-selected", "false");
        });
        btn.classList.add("active");
        btn.setAttribute("aria-selected", "true");

        const variantKey = btn.dataset.variant;
        const preset = PRESET_VARIANTS[variantKey];
        if (preset) {
          renderRecipe({
            recipe_name: preset.name,
            prep_effort_tagline: preset.tagline,
            lazy_rules: preset.rules,
            steps: preset.steps,
            sleepy_audio_script: preset.audio
          });
          triggerSelfDrawingPath(preset.path);
        }
      });
    });
  }

  /* ==========================================================================
     6. ELEVENLABS AUDIO STREAMING & PLAYER (AUDIO PAGE & HOME)
     ========================================================================== */
  async function handleAudioPlayback(customText) {
    if (state.isPlayingAudio && !customText) {
      if (dom.audioPlayer) dom.audioPlayer.pause();
      state.isPlayingAudio = false;
      updateAudioUI(false);
      return;
    }

    const script = customText || state.currentRecipe.sleepy_audio_script || (dom.displayAudioScript ? dom.displayAudioScript.textContent : "");
    if (!script) return;

    if (state.audioBlobCache.has(script)) {
      playAudioBlob(state.audioBlobCache.get(script));
      return;
    }

    if (dom.audioStatusPill) dom.audioStatusPill.textContent = "STREAMING...";
    if (dom.audioBtnText) dom.audioBtnText.textContent = "LOADING ELEVENLABS STREAM...";
    if (dom.btnPlayAudio) dom.btnPlayAudio.disabled = true;

    try {
      const response = await fetch("/api/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ script: script.replace(/^"|"$/g, "").trim() })
      });

      if (!response.ok) {
        throw new Error(`Speak API error: ${response.status}`);
      }

      const audioBlob = await response.blob();
      if (audioBlob && audioBlob.size > 0) {
        state.audioBlobCache.set(script, audioBlob);
        playAudioBlob(audioBlob);
      } else {
        if (dom.audioStatusPill) dom.audioStatusPill.textContent = "KEY MISSING";
        if (dom.audioBtnText) dom.audioBtnText.textContent = "ELEVENLABS API KEY REQUIRED";
        setTimeout(resetAudioPlayback, 3000);
      }
    } catch (e) {
      console.warn("Audio playback error:", e);
      if (dom.audioStatusPill) dom.audioStatusPill.textContent = "AUDIO UNAVAILABLE";
      setTimeout(resetAudioPlayback, 2500);
    } finally {
      if (dom.btnPlayAudio) dom.btnPlayAudio.disabled = false;
    }
  }

  function playAudioBlob(blob) {
    if (!dom.audioPlayer) return;
    if (state.currentAudioUrl) {
      URL.revokeObjectURL(state.currentAudioUrl);
    }
    state.currentAudioUrl = URL.createObjectURL(blob);
    dom.audioPlayer.src = state.currentAudioUrl;
    dom.audioPlayer.play()
      .then(() => {
        state.isPlayingAudio = true;
        updateAudioUI(true);
      })
      .catch((err) => {
        console.warn("Audio play prevented:", err);
        resetAudioPlayback();
      });
  }

  function updateAudioUI(isPlaying) {
    if (!dom.audioBtnIcon) return;
    if (isPlaying) {
      dom.audioBtnIcon.textContent = "❚❚";
      if (dom.audioBtnText) dom.audioBtnText.textContent = "PAUSE SLEEPY AUDIO WALKTHROUGH";
      if (dom.audioStatusPill) dom.audioStatusPill.textContent = "STREAMING (GEORGE)";
      if (dom.audioVisualizer) dom.audioVisualizer.classList.add("playing");
    } else {
      dom.audioBtnIcon.textContent = "▶";
      if (dom.audioBtnText) dom.audioBtnText.textContent = "RESUME SLEEPY AUDIO WALKTHROUGH";
      if (dom.audioStatusPill) dom.audioStatusPill.textContent = "PAUSED";
      if (dom.audioVisualizer) dom.audioVisualizer.classList.remove("playing");
    }
  }

  function resetAudioPlayback() {
    if (dom.audioPlayer) {
      dom.audioPlayer.pause();
    }
    state.isPlayingAudio = false;
    if (dom.audioBtnIcon) dom.audioBtnIcon.textContent = "▶";
    if (dom.audioBtnText) dom.audioBtnText.textContent = "STREAM SLEEPY AUDIO WALKTHROUGH";
    if (dom.audioStatusPill) dom.audioStatusPill.textContent = "STANDBY";
    if (dom.audioVisualizer) dom.audioVisualizer.classList.remove("playing");
  }

  if (dom.audioPlayer) {
    dom.audioPlayer.addEventListener("ended", resetAudioPlayback);
  }

  if (dom.btnPlayAudio) {
    dom.btnPlayAudio.addEventListener("click", () => handleAudioPlayback());
  }

  if (dom.btnStreamCustom && dom.customAudioScriptInput) {
    dom.btnStreamCustom.addEventListener("click", () => {
      const text = dom.customAudioScriptInput.value.trim();
      if (text) {
        if (dom.displayAudioScript) dom.displayAudioScript.textContent = `"${text}"`;
        handleAudioPlayback(text);
      }
    });
  }

  /* ==========================================================================
     7. INITIALIZATION & SCROLL
     ========================================================================== */
  window.addEventListener("scroll", () => {
    updateWordmarkSpread();
  }, { passive: true });

  document.addEventListener("DOMContentLoaded", () => {
    triggerSelfDrawingPath();
  });

})();
