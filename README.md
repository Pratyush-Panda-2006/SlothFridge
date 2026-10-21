# SlothFridge: The Couch Potato Culinary Copilot 🦥🍳

> **Built for the Hacktoberfest Open-Source AI Challenge Week 3**  
> *Theme: Slow and Steady / International Sloth Day*

SlothFridge takes expiring groceries entered by exhausted users lying on their beds and outputs an uncompromisingly lazy, 1-pan or microwave recipe. It uses **TabPFN** to predict cleanup fatigue and continuous standing minutes, **Gemma 2 (via Groq)** to synthesize lazy recipes, and **ElevenLabs** to stream slow, deadpan audio walkthroughs.

---

## 🏛 Architecture & Open Stack

1. **TabPFN Fatigue & Standing Time Engine (`services/tabpfn_service.py`)**:
   - Trained on `data/sloth_meals.csv` (130 realistic kitchen observations).
   - Predicts active standing minutes (continuous regression) and cleanup fatigue tier (`Zero Effort (Mug)`, `Low Effort (1 Pan)`, `High Effort (Avoid)`).
   - Computes utensil penalty and inverted **Sloth Approval Score** (0–100, where higher is lazier).

2. **Gemma 2 Couch Potato Chef (`services/gemma_service.py`)**:
   - Synthesizes lazy recipes using `gemma2-9b-it` on Groq with strict JSON output.
   - Enforces zero cutting boards, hand-tearing ingredients, eating straight from the pan, and 3-step lazy instructions.

3. **ElevenLabs Sleepy Audio Streamer (`services/voice_service.py`)**:
   - Streams deadpan, slow narration using the "George" voice (`eleven_turbo_v2_5`) for hands-free couch guidance.

4. **Multi-Page Mid-Century Maker Frontend (`static/`)**:
   - **The Couch Engine (`index.html`)**: Interactive kitchen ingestion with the SlothFridge hero mascot.
   - **The Thesis (`thesis.html`)**: Editorial breakdown of Gourmet Exhaustion vs 1-Skillet Couch Arbitrage.
   - **Recipe Engine (`recipes.html`)**: Interactive self-drawing SVG effort curves and lazy presets.
   - **Sink Debt Index (`sink-debt.html`)**: Empirical tabular audit and dataset breakdown.
   - **Sleepy Audio (`audio.html`)**: Hands-free audio player with real-time waveform visualizer.

---

## 🚀 Quickstart

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/Pratyush-Panda-2006/SlothFridge.git
cd SlothFridge
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
TABPFN_TOKEN=your_tabpfn_api_key_here
PORT=8000
```

### 3. Launch Local Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 📡 API Endpoints

- `GET /api/health`: Health status of the SlothFridge engine.
- `POST /api/cook`: Analyzes ingredients via TabPFN and synthesizes recipes via Gemma 2.
- `POST /api/speak`: Streams slow, deadpan audio narration via ElevenLabs.

---

## 📜 License
MIT License. Built with ❤️ and minimal vertical posture for Hacktoberfest.
