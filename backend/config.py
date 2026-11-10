import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Gnani.ai Configurations
GNANI_API_KEY = os.getenv("GNANI_API_KEY", "vach_1ytE2CY5X2DTieGs5rg6UuEzVpXTmyggYfZHnBaShYrg3y5g13OepP4oKxyJ3b313G5ami8F1DD7z39GHRCgx9Jqr8pveGhP_1e2ebfc040b8f4bbfaa487f60abee260")
GNANI_STT_WS_URL = os.getenv("GNANI_STT_WS_URL", "wss://api.vachana.ai/stt/v3/stream")
GNANI_LANGUAGE = "kn-IN"  # Kannada telephony
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1

# Decision Thresholds (Golden 45-60s Window)
THRESHOLD_SAFE = 0.35        # Below 35%: Green / Normal call
THRESHOLD_SUSPICIOUS = 0.70  # 35% - 70%: Yellow / Amber Warning (Pre-emptive advisory)
                             # Above 70%: Red / Critical Scam Alert

# Trained Model Paths (From Colab Export)
MDEBERTA_MODEL_PATH = os.path.join(MODELS_DIR, "mdeberta_scam_model")
SETFIT_MODEL_PATH = os.path.join(MODELS_DIR, "setfit_intent_model")
INTENT_CLASSIFIER_PKL = os.path.join(MODELS_DIR, "intent_classifier.pkl")
XGBOOST_MODEL_PATH = os.path.join(MODELS_DIR, "xgboost_scam_model.json")
FEATURE_CONFIG_PATH = os.path.join(MODELS_DIR, "feature_config.json")
