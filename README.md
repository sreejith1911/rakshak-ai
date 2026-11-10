# RakshakAI — Real-Time Kanglish Scam Call Detector

> **Gnani.ai Hackathon 2026** | Real-time Kannada + English telephony scam interception

[![Deploy](https://img.shields.io/badge/demo-live-brightgreen)](https://your-username.github.io/rakshak-ai)
[![Backend](https://img.shields.io/badge/backend-render.com-blue)](https://rakshak-ai.onrender.com)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

---

## What it does

RakshakAI listens to a live phone call in **Kannada or Kanglish (Kannada+English)** and detects scam patterns in real time — before the victim hangs up.

- 🎙️ **Gnani Prisma STT** (`kn-IN`) for live Kannada speech recognition  
- 🤖 **Multilingual Sentence Embeddings** (`paraphrase-multilingual-MiniLM-L12-v2`) + XGBoost ensemble  
- 🧠 **Behavioral Semantic Bank** — catches scams with zero keywords (bribery, coercion, implausible authority)  
- ⚡ **< 15ms** inference latency per turn  
- 🚨 **3-tier progressive alerts**: Green → Amber → Red within 60 seconds  

## Architecture

```
Mic (browser) 
  → Gnani Prisma STT (kn-IN WebSocket)
  → Turn segmentation
  → Parallel:
      A. Regex feature extractor (9 heuristic features)
      B. Multilingual embedder → Logistic Regression head (intent prob)
      C. Behavioral semantic similarity bank (OOB scam pattern detection)
  → XGBoost stacking ensemble
  → EMA temporal risk accumulator
  → 3-tier alert (Safe / Warning / Critical)
  → WebSocket push to dashboard
```

## Stack

| Layer | Technology |
|---|---|
| ASR | Gnani Prisma STT `kn-IN` / Web Speech API fallback |
| Backend | FastAPI + Uvicorn (Python 3.11+) |
| ML Models | XGBoost + `paraphrase-multilingual-MiniLM-L12-v2` |
| Frontend | Vanilla JS + Web Audio API + Canvas |
| Training | Google Colab (see `gnani_scam_detector_colab.ipynb`) |

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/rakshak-ai
cd rakshak-ai
pip install -r requirements.txt

# Optional: place trained models in models/ directory
# models/intent_classifier.pkl
# models/xgboost_scam_model.json

python run_app.py
# Open http://localhost:8080
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GNANI_API_KEY` | Optional | Gnani Prisma STT API key (get from hackathon portal) |
| `PORT` | Optional | Server port (default: 8080) |

## Training

Open `gnani_scam_detector_colab.ipynb` in Google Colab.  
Trains on:
- `chinna887/Indian_Cyber_Scam_PhoneCall_Hinglish_Dataset` (10,000 records)
- `anmolshrivastav/scam-ham-india` (2,272 records)

Exports `gnani_scam_models.zip` → place contents in `models/`.

## Deployment

- **Frontend**: GitHub Pages (auto-deployed via GitHub Actions)  
- **Backend**: Render.com / Railway / HuggingFace Spaces  
- See `.github/workflows/` for CI/CD pipeline

## License

MIT
