import os
import json
import logging
from typing import Dict, Any, List, Optional
from backend.config import (
    SETFIT_MODEL_PATH,
    MDEBERTA_MODEL_PATH,
    INTENT_CLASSIFIER_PKL,
    XGBOOST_MODEL_PATH,
    THRESHOLD_SAFE,
    THRESHOLD_SUSPICIOUS
)
from backend.feature_extractor import ScamFeatureExtractor
from backend.behavioral_detector import behavioral_detector

logger = logging.getLogger("model_runner")
logging.basicConfig(level=logging.INFO)

class ScamDetectionEngine:
    """
    Unified Inference Engine:
    - Auto-detects Colab-trained models if placed in models/
    - Otherwise runs built-in Smart Heuristic Stacking Engine (instant zero-dependency demo!)
    - Maintains conversational state and Temporal Bayesian/EMA Risk Accumulator.
    """
    def __init__(self):
        self.extractor = ScamFeatureExtractor()
        self.trained_models_loaded = False
        self.intent_model = None
        self.xgb_model = None

        self._try_load_trained_models()

    def _try_load_trained_models(self):
        """Attempts to load trained weights exported from Google Colab / Kaggle."""
        try:
            import xgboost as xgb
            
            # Check 0: Fine-Tuned mDeBERTa-v3 Model Directory
            if os.path.exists(MDEBERTA_MODEL_PATH):
                logger.info(f"Loading Fine-Tuned mDeBERTa-v3 from {MDEBERTA_MODEL_PATH}...")
                from transformers import AutoModelForSequenceClassification, AutoTokenizer
                self.mdeberta_tokenizer = AutoTokenizer.from_pretrained(MDEBERTA_MODEL_PATH)
                self.mdeberta_model = AutoModelForSequenceClassification.from_pretrained(MDEBERTA_MODEL_PATH)
                self.mdeberta_model.eval()
                self.model_type = "mdeberta"
                self.trained_models_loaded = True
                logger.info("[SUCCESS] FINE-TUNED mDeBERTa-v3 SCAM MODEL LOADED!")

            # Check 1: Language-Independent Classifier (intent_classifier.pkl + SentenceTransformer)
            elif os.path.exists(XGBOOST_MODEL_PATH) and os.path.exists(INTENT_CLASSIFIER_PKL):
                logger.info(f"Loading trained XGBoost model from {XGBOOST_MODEL_PATH}...")
                self.xgb_model = xgb.Booster()
                self.xgb_model.load_model(XGBOOST_MODEL_PATH)

                logger.info(f"Loading Language-Independent Intent Classifier from {INTENT_CLASSIFIER_PKL}...")
                import pickle
                import threading
                with open(INTENT_CLASSIFIER_PKL, "rb") as f:
                    self.intent_classifier = pickle.load(f)

                self.embedder = None
                self.model_type = "multilingual_embedding_head"

                def _load_embedder_bg():
                    try:
                        logger.info("Initializing SentenceTransformer in background...")
                        from sentence_transformers import SentenceTransformer
                        self.embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
                        self.trained_models_loaded = True
                        # Wire embedder into behavioral detector (pre-encodes the bank)
                        behavioral_detector.set_embedder(self.embedder)
                        logger.info("[SUCCESS] LANGUAGE-INDEPENDENT COLAB MODELS + BEHAVIORAL DETECTOR READY!")
                    except Exception as e:
                        logger.warning(f"Error loading embedder: {e}")

                threading.Thread(target=_load_embedder_bg, daemon=True).start()

            # Check 2: Alternative SetFit Model Directory
            elif os.path.exists(XGBOOST_MODEL_PATH) and os.path.exists(SETFIT_MODEL_PATH):
                logger.info(f"Loading trained XGBoost model from {XGBOOST_MODEL_PATH}...")
                self.xgb_model = xgb.Booster()
                self.xgb_model.load_model(XGBOOST_MODEL_PATH)

                logger.info(f"Loading trained SetFit model from {SETFIT_MODEL_PATH}...")
                from setfit import SetFitModel
                self.intent_model = SetFitModel.from_pretrained(SETFIT_MODEL_PATH)

                self.trained_models_loaded = True
                self.model_type = "setfit"
                logger.info("[SUCCESS] LOADED TRAINED SETFIT COLAB MODELS!")
            else:
                logger.info("[INFO] Trained Colab models not detected. Running built-in Smart Stacking Engine.")
        except Exception as e:
            logger.warning(f"Error loading trained models: {e}. Falling back to smart stacking engine.")
            self.trained_models_loaded = False

    def predict_turn(
        self,
        text: str,
        turn_index: int = 1,
        prev_cumulative_risk: float = 0.0,
        dialogue_history: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyzes a single conversational turn in streaming context.
        """
        # 1. Feature Extraction (Regex / Domain Heuristics)
        h_features, pills = self.extractor.extract_features(text, turn_idx=turn_index)

        # 1b. Behavioral Semantic Detection (catches scams with no explicit keywords)
        behavioral_score, behavioral_flags = behavioral_detector.score_turn(text)
        # Merge behavioral pills into pills list (avoid duplicate categories)
        existing_cats = {p["category"] for p in pills}
        for bf in behavioral_flags:
            if bf["category"] not in existing_cats:
                pills.append({
                    "category": bf["category"],
                    "severity": bf["severity"],
                    "keywords": [f"semantic match ({bf['score']:.2f})"],
                    "score": bf["score"]
                })
                existing_cats.add(bf["category"])

        # 2. Intent Probability
        intent_prob = None
        if self.trained_models_loaded:
            try:
                eval_text = " ".join((dialogue_history or []) + [text])
                if hasattr(self, "model_type") and self.model_type == "mdeberta":
                    import torch
                    import torch.nn.functional as F
                    inputs = self.mdeberta_tokenizer(eval_text, return_tensors="pt", truncation=True, max_length=128)
                    with torch.no_grad():
                        outputs = self.mdeberta_model(**inputs)
                        probs = F.softmax(outputs.logits, dim=-1).squeeze().cpu().numpy()
                        intent_prob = float(probs[1]) if probs.ndim > 0 else float(probs)
                elif hasattr(self, "model_type") and self.model_type == "multilingual_embedding_head":
                    emb = self.embedder.encode([eval_text])
                    probs = self.intent_classifier.predict_proba(emb)
                    intent_prob = float(probs[0][1]) if probs.ndim > 1 else float(probs[0])
                elif hasattr(self, "intent_model") and self.intent_model:
                    probs = self.intent_model.predict_proba([eval_text])
                    if hasattr(probs, 'numpy'):
                        probs = probs.numpy()
                    intent_prob = float(probs[0][1]) if probs.ndim > 1 else float(probs[0])
            except Exception as e:
                logger.warning(f"Trained intent inference error: {e}")
                intent_prob = None

        if intent_prob is None:
            intent_prob = self._heuristic_intent_score(h_features)

        # Boost intent_prob with behavioral semantic score when keywords miss
        # This handles "Pay me cash to drop the case" with zero keyword matches
        if behavioral_score > 0.0:
            intent_prob = max(intent_prob, behavioral_score * 0.85)

        # 3. XGBoost Ensemble Stacking
        if self.trained_models_loaded and self.xgb_model:
            try:
                import xgboost as xgb
                import numpy as np
                feat_array = np.array([[intent_prob] + h_features])
                dmatrix = xgb.DMatrix(feat_array)
                preds = self.xgb_model.predict(dmatrix)
                turn_risk = float(preds[0])
            except Exception as e:
                logger.warning(f"XGBoost inference error: {e}")
                turn_risk = self._combine_turn_risk(intent_prob, h_features)
        else:
            turn_risk = self._combine_turn_risk(intent_prob, h_features)

        # 4. Temporal Bayesian / EMA Risk Accumulator
        # Alpha = 0.55: smooths noise but accelerates rapidly when sustained hostility appears
        alpha = 0.55
        if prev_cumulative_risk == 0.0:
            cumulative_risk = turn_risk
        else:
            # If a turn has an active critical trigger (OTP or AnyDesk), boost immediately
            has_critical = any(p["severity"] == "critical" for p in pills)
            boost = 0.15 if has_critical else 0.0
            cumulative_risk = (alpha * prev_cumulative_risk) + ((1.0 - alpha) * turn_risk) + boost
            cumulative_risk = min(max(cumulative_risk, 0.0), 1.0)

        # 5. Determine Alert Tier
        if cumulative_risk < THRESHOLD_SAFE:
            tier = "SAFE"
            tier_label = "Call Secure 🟢"
            status_color = "emerald"
            advice = "Normal conversational pattern. No threats detected."
        elif cumulative_risk < THRESHOLD_SUSPICIOUS:
            tier = "AMBER_WARNING"
            tier_label = "Suspicious Call - Caution Advised 🟡"
            status_color = "amber"
            advice = "High-pressure tactics or authority impersonation detected. Do NOT install apps or share credentials."
        else:
            tier = "CRITICAL_SCAM"
            tier_label = "CRITICAL SCAM DETECTED 🔴"
            status_color = "rose"
            advice = "FRAUD IN PROGRESS! Scammer demanding remote access or financial transfer. HANG UP IMMEDIATELY!"

        return {
            "turn_index": turn_index,
            "text": text,
            "intent_prob": round(intent_prob, 3),
            "turn_risk": round(turn_risk, 3),
            "cumulative_risk": round(cumulative_risk, 3),
            "tier": tier,
            "tier_label": tier_label,
            "status_color": status_color,
            "pills": pills,
            "advice": advice,
            "models_source": "colab_trained" if self.trained_models_loaded else "smart_stacking_engine"
        }

    def _heuristic_intent_score(self, h_feats: List[float]) -> float:
        """Calibrated fallback intent score based on feature weighting."""
        auth, urg, cred, apk, fin, iso, indic, turn_idx_norm, word_norm = h_feats
        score = (
            0.25 * auth +
            0.20 * urg +
            0.25 * cred +
            0.30 * apk +
            0.20 * fin +
            0.25 * iso +
            0.05 * indic
        )
        return min(max(score, 0.05), 0.98)

    def _combine_turn_risk(self, intent_prob: float, h_feats: List[float]) -> float:
        """Ensemble weighting of intent prob and structural heuristics."""
        auth, urg, cred, apk, fin, iso, _, _, _ = h_feats
        # Heavy penalty for critical scam vectors
        critical_boost = 0.25 if (apk > 0.0 or cred > 0.0 or iso > 0.0) else 0.0
        combined = (0.55 * intent_prob) + (0.25 * auth) + (0.20 * urg) + critical_boost
        return min(max(combined, 0.02), 0.99)

# Global engine instance
engine = ScamDetectionEngine()
