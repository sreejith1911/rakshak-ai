# 🛡️ RakshakAI — Real-Time Kanglish Scam Call Interceptor

> **Gnani.ai Hackathon 2026** | Real-time Kannada + English Telephony Scam Interceptor

[![Live Demo](https://img.shields.io/badge/Demo-GitHub%20Pages%20Live-brightgreen?style=for-the-badge&logo=github)](https://sreejith1911.github.io/rakshak-ai/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sreejith1911/rakshak-ai/blob/master/mdeberta_scam_detector_colab.ipynb)
[![CI Pipeline](https://github.com/sreejith1911/rakshak-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/sreejith1911/rakshak-ai/actions/workflows/ci.yml)
[![Pages Deployment](https://github.com/sreejith1911/rakshak-ai/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/sreejith1911/rakshak-ai/actions/workflows/deploy-pages.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## What It Does

RakshakAI listens to a live telephony stream in **Kannada or Kanglish (`kn-IN`)** and intercepts financial cyber frauds within the **45–60s Golden Decision Horizon** — before the victim transfers money or downloads remote-access malware.

- 🎙️ **Gnani Prisma STT (`kn-IN`)**: Live streaming telephony speech-to-text.
- 🤖 **Multilingual DeBERTa-v3 (`mDeBERTa-v3-base`)**: Zero-shot cross-lingual intent and behavioral coercion classifier trained on 12,000+ real Indian cyber fraud calls (Hinglish + English) evaluating native Kannada Unicode text without runtime translation.
- 🧠 **Behavioral Semantic Reasoning Bank**: Catches out-of-distribution scams with zero keyword matches (e.g., implausible police extortion, private bribery, artificial deadlines).
- ⚡ **Ultra-Low Latency**: < 25ms inference per conversational turn.
- 🚨 **3-Tier Progressive Alert Horizon**: Safe (Green) → Advisory Warning (Amber) → Critical Fraud (Red).

---

## 🏛️ Architecture

```
[Live Telephone Call]
        │
        ▼ (Web Audio API 16kHz PCM)
[Gnani Prisma STT kn-IN WebSocket]
        │
        ▼ (Turn-by-turn Kannada text)
┌─────────────────────────────────────────────────────────────┐
│                 Real-Time Inference Engine                  │
│                                                             │
│   A. Heuristic Red Flag Extractor (9 Features)              │
│      - Authority, Urgency, OTP/PIN, AnyDesk, Fin, Isolation │
│                                                             │
│   B. Fine-Tuned mDeBERTa-v3 / Multilingual Embedder        │
│      - Zero-shot cross-lingual intent probability           │
│                                                             │
│   C. Behavioral Semantic Similarity Bank                    │
│      - Catches subtle extortion / coercion without keywords │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
              [XGBoost & Temporal Bayesian EMA]
                               │
                               ▼
             [3-Tier Progressive Threat Alert]
                🟢 Safe | 🟡 Amber | 🔴 Red
                               │
                               ▼
        [Real-Time WebSocket Push to Web Dashboard]
```

---

## 🚀 Quick Start (Local Run)

```bash
# 1. Clone repository
git clone https://github.com/sreejith1911/rakshak-ai.git
cd rakshak-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch unified server
python run_app.py
```
Open **[http://localhost:8080](http://localhost:8080)** in Chrome or Edge and click **"Start Live Mic"**.

---

## 📓 Model Training (Google Colab)

Click the badge to open the fine-tuning notebook directly on a free Google Colab T4 GPU:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sreejith1911/rakshak-ai/blob/master/mdeberta_scam_detector_colab.ipynb)

### Training Highlights:
- **Datasets**: 
  - `chinna887/Indian_Cyber_Scam_PhoneCall_Hinglish_Dataset` (10,000 real Indian cyber fraud transcripts)
  - `anmolshrivastav/scam-ham-india` (2,272 SMS/telecom Indian communications)
- **Zero-Shot Cross-Lingual Transfer**: Evaluated against native Kannada test phrases (`"50,000 ಕೊಟ್ಟ್ರೆ ಕೇಸ್ ಇಂದ ಬಿಡ್ತೀವಿ"`, `"ಡ್ರಗ್ ಪಾರ್ಸಲ್ ಸಿಕ್ಕಿದೆ"`).
- **Export**: Automatically exports `rakshak_mdeberta_model.zip` ready to drop into the `models/` folder.

---

## 🌐 Live Deployments & CI/CD

- **Frontend Dashboard**: Deployed automatically to GitHub Pages at:  
  **[https://sreejith1911.github.io/rakshak-ai/](https://sreejith1911.github.io/rakshak-ai/)**
- **Continuous Integration**: `.github/workflows/ci.yml` validates fraud heuristic test suites on every commit.
- **Continuous Deployment**: `.github/workflows/deploy-pages.yml` deploys updates to GitHub Pages on every push.
- **Docker / Cloud Backend**: Includes `Dockerfile` and `render.yaml` for 1-click deployment to Render or Railway.

---

## 📜 License
MIT License. Built for the Gnani.ai Hackathon 2026.
