"""
Behavioral Semantic Scam Detector
----------------------------------
Uses cosine similarity against a curated "scam behavior bank" of reference
sentences. Works in ANY language (Kannada, Kanglish, Hindi, English) because
the multilingual sentence embedder maps them all to the same vector space.

Catches behavioral red flags with ZERO keyword matching:
  - "Pay me 50,000 and I'll drop the case"  -> bribery/extortion
  - "Come to the station in one hour"        -> artificial urgency
  - "Don't tell anyone about this call"      -> isolation tactic
  - "I'll arrest you if you don't pay"       -> threat/coercion

Latency: ~15-25ms per turn (after embedder is warm).
"""

import numpy as np
from typing import List, Tuple, Optional

# ---------------------------------------------------------------------------
# Default threshold: 0.38 catches short Kannada sentences (5-8 words)
# without meaningfully increasing false positives on safe calls.
# Safe baseline tops out at ~0.37 in testing.
# ---------------------------------------------------------------------------
DEFAULT_THRESHOLD = 0.38

SCAM_BEHAVIOR_BANK = [
    # --- Bribery / Financial Extortion ---
    ("Pay me money and I will drop the case against you", "Bribery / Extortion", "critical"),
    ("Give me cash and your problem will be solved", "Bribery / Extortion", "critical"),
    ("If you transfer the amount the case will be closed", "Bribery / Extortion", "critical"),
    ("Pay the fine directly to me and you will be safe", "Bribery / Extortion", "critical"),
    ("Send the money within the hour to avoid legal action", "Bribery / Extortion", "critical"),
    ("Pay me and I will remove your name from the case", "Bribery / Extortion", "critical"),

    # --- Implausible Authority Behavior ---
    ("A government officer is calling you to ask for personal payment", "Authority Abuse", "high"),
    ("The officer is demanding cash to settle the matter privately", "Authority Abuse", "high"),
    ("Police calling to settle a case without filing an official report", "Authority Abuse", "high"),
    ("Officer threatening arrest unless you pay money immediately", "Authority Abuse", "critical"),
    ("Real police do not ask for money over the phone", "Authority Abuse", "high"),

    # --- Urgency and Deadline Pressure ---
    ("You must act right now or serious consequences will follow", "Urgency Pressure", "medium"),
    ("You have very little time before we take action against you", "Urgency Pressure", "medium"),
    ("Come immediately to the station or we will send officers", "Urgency Pressure", "high"),
    ("This is your last chance to resolve this matter", "Urgency Pressure", "medium"),
    ("If you do not cooperate in the next hour we will proceed", "Urgency Pressure", "high"),
    ("Come quickly right now there is no time", "Urgency Pressure", "medium"),
    ("You have one hour to pay otherwise action will be taken", "Urgency Pressure", "high"),

    # --- Threat and Coercion ---
    ("I will put a criminal case on you if you don't comply", "Threat / Coercion", "critical"),
    ("Your name will appear in a drug trafficking case", "Threat / Coercion", "critical"),
    ("You will go to jail for many years if you don't pay", "Threat / Coercion", "critical"),
    ("We found illegal items linked to your identity", "Threat / Coercion", "high"),
    ("I will arrest you if you do not cooperate", "Threat / Coercion", "critical"),
    ("Otherwise we will take legal action against you immediately", "Threat / Coercion", "critical"),
    ("You will be arrested if you do not pay the amount", "Threat / Coercion", "critical"),
    ("We are filing a case against you right now", "Threat / Coercion", "critical"),
    ("We will send police to your house if you don't respond", "Threat / Coercion", "critical"),
    ("Do not refuse or consequences will be very serious for you", "Threat / Coercion", "high"),

    # --- Isolation Tactics ---
    ("Do not tell anyone about this call it is confidential", "Isolation Tactic", "high"),
    ("Keep this conversation between us or the situation will worsen", "Isolation Tactic", "high"),
    ("Do not consult a lawyer this is an internal matter", "Isolation Tactic", "high"),
    ("Stay on the call and do not speak to anyone else", "Isolation Tactic", "medium"),
    ("Do not disconnect the call stay with me", "Isolation Tactic", "medium"),

    # --- Implausible Scenario Setup ---
    ("Your Aadhaar card was used to send drugs across the border", "Implausible Scenario", "high"),
    ("A parcel in your name was seized at the airport with contraband", "Implausible Scenario", "high"),
    ("Your bank account is linked to a money laundering operation", "Implausible Scenario", "high"),
    ("We have evidence your identity was used for illegal activity", "Implausible Scenario", "medium"),
    ("A drug parcel registered under your name has been intercepted", "Implausible Scenario", "high"),

    # --- Social Engineering / False Rescue ---
    ("I am trying to help you but you must do exactly as I say", "Social Engineering", "medium"),
    ("Trust me I am on your side but we need to act fast", "Social Engineering", "medium"),
    ("I can protect you from this case but only if you cooperate now", "Social Engineering", "high"),
]


class BehavioralScamDetector:
    """
    Semantic similarity-based behavioral scam detector.
    Requires the sentence embedder to be injected (already loaded by model_runner).
    Falls back gracefully if embedder is not yet ready.
    """

    def __init__(self):
        self._bank_embeddings: Optional[np.ndarray] = None
        self._labels = [(text, category, severity) for text, category, severity in SCAM_BEHAVIOR_BANK]
        self._embedder = None

    def set_embedder(self, embedder):
        """Called by model_runner once SentenceTransformer finishes loading."""
        self._embedder = embedder
        self._precompute_bank()

    def _precompute_bank(self):
        """Pre-encode all reference sentences once at startup. ~30ms total."""
        texts = [t for t, _, _ in SCAM_BEHAVIOR_BANK]
        self._bank_embeddings = self._embedder.encode(texts, normalize_embeddings=True)

    def score_turn(self, text: str, threshold: float = DEFAULT_THRESHOLD) -> Tuple[float, List[dict]]:
        """
        Returns:
            behavioral_score  : float in [0, 1] - max cosine similarity vs bank
            behavioral_flags  : list of matched behavior categories with scores
        """
        if self._embedder is None or self._bank_embeddings is None:
            return 0.0, []

        try:
            turn_emb = self._embedder.encode([text], normalize_embeddings=True)
            # Cosine similarity = dot product since both are L2-normalized
            similarities = (self._bank_embeddings @ turn_emb.T).flatten()

            behavioral_score = float(np.max(similarities))
            flags = []

            # Collect all matches above threshold (deduplicated by category)
            seen_categories = set()
            for idx in np.argsort(similarities)[::-1]:
                sim = float(similarities[idx])
                if sim < threshold:
                    break
                _, category, severity = self._labels[idx]
                if category not in seen_categories:
                    flags.append({
                        "category": category,
                        "severity": severity,
                        "score": round(sim, 3),
                        "matched_ref": SCAM_BEHAVIOR_BANK[idx][0][:60] + "..."
                    })
                    seen_categories.add(category)

            return behavioral_score, flags

        except Exception:
            return 0.0, []


# Global singleton - shared with model_runner
behavioral_detector = BehavioralScamDetector()
