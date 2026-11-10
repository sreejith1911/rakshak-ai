import re
from typing import Dict, List, Tuple, Any

class ScamFeatureExtractor:
    """
    Ultra-low-latency (<0.5ms) Regex & Heuristic Feature Extractor.
    Extracts 9 behavioral fraud indicators designed for Indian / Kanglish scams.
    Handles BOTH romanized English/Kanglish AND native Kannada Unicode script
    (since kn-IN STT outputs Kannada script: ಸಿಬಿಐ, ಒಟಿಪಿ, etc.)
    """
    def __init__(self):

        # 1. Authority Impersonation
        # Kannada script: police=ಪೊಲೀಸ್, CBI=ಸಿಬಿಐ, officer=ಆಫೀಸರ್,
        #   court=ಕೋರ್ಟ್, arrest=ಅರೆಸ್ಟ್, TRAI=ಟ್ರಾಯ್, RBI=ಆರ್‌ಬಿಐ,
        #   customs=ಕಸ್ಟಮ್ಸ್, judge=ಜಡ್ಜ್, inspector=ಇನ್ಸ್ಪೆಕ್ಟರ್
        self.authority_patterns = re.compile(
            r'(?:'
            # English / Romanized
            r'\b(police|cbi|inspector|patil|customs|court|judge|arrest\s*warrant|trai|rbi|'
            r'cyber\s*crime|crime\s*branch|dcp|officer|mumbai\s*police|delhi\s*police|enforcement)\b'
            r'|'
            # Kannada Unicode script
            r'(ಪೊಲೀಸ್|ಸಿಬಿಐ|ಆಫೀಸರ್|ಅಧಿಕಾರಿ|ಕೋರ್ಟ್|ಕೋರ್ಟು|ಅರೆಸ್ಟ್|ಟ್ರಾಯ್|ಆರ್\u200cಬಿಐ|'
            r'ಕಸ್ಟಮ್ಸ್|ಜಡ್ಜ್|ಇನ್ಸ್ಪೆಕ್ಟರ್|ಮುಂಬೈ\s*ಪೊಲೀಸ್|ಸಿಐಡಿ|ಇಡಿ|ಜಾರಿ\s*ನಿರ್ದೇಶನಾಲಯ)'
            r')',
            re.IGNORECASE
        )

        # 2. Urgency & Coercion
        # Kannada: immediately=ತಕ್ಷಣ/ಬೇಗ, arrest=ಅರೆಸ್ಟ್, freeze=ಫ್ರೀಜ್,
        #   block=ಬ್ಲಾಕ್, disconnect=ಡಿಸ್ಕನೆಕ್ಟ್, quick=ಬೇಗ/ಶೀಘ್ರ
        self.urgency_patterns = re.compile(
            r'(?:'
            r'\b(immediately|urgent|arrest|within\s*\d+|tonight|freeze|permanently|'
            r'penalty|quick|fast|right\s*now|disconnect|block|last\s*chance|warning)\b'
            r'|'
            r'(ತಕ್ಷಣ|ಬೇಗ|ಅರೆಸ್ಟ್|ಫ್ರೀಜ್|ಬ್ಲಾಕ್|ಡಿಸ್ಕನೆಕ್ಟ್|ಶೀಘ್ರ|ತಡ\s*ಮಾಡಬೇಡಿ|'
            r'ಸಮಯ\s*ಇಲ್ಲ|ಎಚ್ಚರಿಕೆ|ನಿರ್ಬಂಧ|ರದ್ದು)'
            r')',
            re.IGNORECASE
        )

        # 3. Credential Solicitation
        # Kannada: OTP=ಒಟಿಪಿ, PIN=ಪಿನ್, password=ಪಾಸ್‌ವರ್ಡ್,
        #   aadhar=ಆಧಾರ್/ಅಧಾರ್, PAN=ಪ್ಯಾನ್, card=ಕಾರ್ಡ್
        self.credential_patterns = re.compile(
            r'(?:'
            r'\b(otp|pin|cvv|password|card\s*number|aadhaar|aadhar|pan\s*card|pan\s*number|'
            r'debit\s*card|credit\s*card|expiry\s*date|account\s*number)\b'
            r'|'
            r'(ಒಟಿಪಿ|ಓಟಿಪಿ|ಪಿನ್|ಪಾಸ್\u200cವರ್ಡ್|ಆಧಾರ್|ಅಧಾರ್|ಆಧಾರ|ಪ್ಯಾನ್\s*ಕಾರ್ಡ್|'
            r'ಡೆಬಿಟ್\s*ಕಾರ್ಡ್|ಕ್ರೆಡಿಟ್\s*ಕಾರ್ಡ್|ಅಕೌಂಟ್\s*ನಂಬರ್|ಕಾರ್ಡ್\s*ನಂಬರ್|ಶೇರ್\s*ಮಾಡಿ)'
            r')',
            re.IGNORECASE
        )

        # 4. Remote Access & APK Fraud
        # Kannada: AnyDesk=ಅನಿಡೆಸ್ಕ್, download=ಡೌನ್‌ಲೋಡ್,
        #   install=ಇನ್ಸ್ಟಾಲ್, screen share=ಸ್ಕ್ರೀನ್ ಶೇರ್
        self.remote_apk_patterns = re.compile(
            r'(?:'
            r'\b(anydesk|teamviewer|quicksupport|rustdesk|apk|download\s*app|play\s*store|'
            r'remote\s*kyc|screen\s*share|install|remote\s*access)\b'
            r'|'
            r'(ಅನಿಡೆಸ್ಕ್|ಡೌನ್\u200cಲೋಡ್|ಇನ್ಸ್ಟಾಲ್|ಸ್ಕ್ರೀನ್\s*ಶೇರ್|ರಿಮೋಟ್|ಅಪ್ಲಿಕೇಶನ್\s*ಡೌನ್\u200cಲೋಡ್)'
            r')',
            re.IGNORECASE
        )

        # 5. Financial Demands & Money Extraction
        # Kannada: transfer=ಟ್ರಾನ್ಸ್ಫರ್, bank=ಬ್ಯಾಂಕ್,
        #   money=ಹಣ, fine=ದಂಡ, bail=ಜಾಮೀನು
        self.financial_patterns = re.compile(
            r'(?:'
            r'\b(transfer|security\s*deposit|refund|bank\s*account|pay|money\s*laundering|'
            r'cashback|reward\s*points|rupees|fine|charges|bail|payment|wallet)\b'
            r'|'
            r'(ಟ್ರಾನ್ಸ್ಫರ್|ಬ್ಯಾಂಕ್\s*ಅಕೌಂಟ್|ಹಣ|ದಂಡ|ಜಾಮೀನು|ಪಾವತಿ|ರೂಪಾಯಿ|'
            r'ವಾಲೆಟ್|ಮನಿ\s*ಲಾಂಡರಿಂಗ್|ರಿಫಂಡ್)'
            r')',
            re.IGNORECASE
        )

        # 6. Isolation & Psychological Secrecy
        # Kannada: digital arrest=ಡಿಜಿಟಲ್ ಅರೆಸ್ಟ್,
        #   secret=ರಹಸ್ಯ, don't tell=ಹೇಳಬೇಡಿ, video call=ವಿಡಿಯೋ ಕಾಲ್
        self.isolation_patterns = re.compile(
            r'(?:'
            r'\b(digital\s*arrest|private\s*room|don\'t\s*disconnect|do\s*not\s*disconnect|'
            r'quiet\s*room|don\'t\s*tell|secret|confidential|video\s*call|stay\s*online)\b'
            r'|'
            r'(ಡಿಜಿಟಲ್\s*ಅರೆಸ್ಟ್|ರಹಸ್ಯ|ಹೇಳಬೇಡಿ|ವಿಡಿಯೋ\s*ಕಾಲ್|ಕಟ್\s*ಮಾಡಬೇಡಿ|'
            r'ಪ್ರೈವೇಟ್|ಗೌಪ್ಯ|ಒಬ್ಬರೇ\s*ಇರಿ)'
            r')',
            re.IGNORECASE
        )

        # 7. Kanglish / Kannada Telephony Trigger Markers (romanized + script)
        # Common Kannada verbs/words that only appear in suspicious telephony contexts
        self.indic_triggers = re.compile(
            r'(?:'
            r'\b(aagide|maadtidivi|kalsi|barutte|cut\s*aagatte|banndide|nimma|illi|nodri|'
            r'eegle|maadi|beega|bega|haangi|hoogatte|irutteera)\b'
            r'|'
            r'(ಆಗಿದೆ|ಮಾಡ್ತಿದ್ದೀವಿ|ಬರುತ್ತೆ|ನಿಮ್ಮ|ಇಲ್ಲಿ|ನೋಡ್ರಿ|ಮಾಡಿ|ಕೇಸ್|ರಿಜಿಸ್ಟರ್|'
            r'ಪಾರ್ಸಲ್|ಡ್ರಗ್)'
            r')',
            re.IGNORECASE
        )

    def extract_features(self, text: str, turn_idx: int = 1) -> Tuple[List[float], List[Dict[str, Any]]]:
        """
        Returns:
            - feature_vector: 9 floats normalized in [0, 1]
            - matched_pills: List of human-readable explanation pills for UI
        """
        def find_all(pattern, text):
            """Flatten all match groups and return unique non-empty matches."""
            return list(set(
                m for group in pattern.findall(text)
                for m in (group if isinstance(group, tuple) else [group])
                if m
            ))

        auth_matches  = find_all(self.authority_patterns,  text)
        urg_matches   = find_all(self.urgency_patterns,    text)
        cred_matches  = find_all(self.credential_patterns, text)
        apk_matches   = find_all(self.remote_apk_patterns, text)
        fin_matches   = find_all(self.financial_patterns,  text)
        iso_matches   = find_all(self.isolation_patterns,  text)
        indic_matches = find_all(self.indic_triggers,      text)

        word_count = len(text.split())

        # Vector normalized in [0, 1]
        feature_vector = [
            min(len(auth_matches) / 2.0, 1.0),
            min(len(urg_matches)  / 2.0, 1.0),
            1.0 if cred_matches  else 0.0,
            1.0 if apk_matches   else 0.0,
            min(len(fin_matches) / 2.0, 1.0),
            1.0 if iso_matches   else 0.0,
            1.0 if indic_matches else 0.0,
            min(turn_idx / 6.0,    1.0),
            min(word_count / 40.0, 1.0)
        ]

        # Generate explainability pills for UI
        pills = []
        if auth_matches:
            pills.append({
                "category": "Authority Impersonation",
                "severity": "high",
                "keywords": auth_matches,
                "score": round(feature_vector[0], 2)
            })
        if urg_matches:
            pills.append({
                "category": "Urgency & Pressure",
                "severity": "medium",
                "keywords": urg_matches,
                "score": round(feature_vector[1], 2)
            })
        if cred_matches:
            pills.append({
                "category": "Credential Theft (OTP/PIN)",
                "severity": "critical",
                "keywords": cred_matches,
                "score": 1.0
            })
        if apk_matches:
            pills.append({
                "category": "Remote APK / AnyDesk",
                "severity": "critical",
                "keywords": apk_matches,
                "score": 1.0
            })
        if fin_matches:
            pills.append({
                "category": "Financial Extraction Demand",
                "severity": "high",
                "keywords": fin_matches,
                "score": round(feature_vector[4], 2)
            })
        if iso_matches:
            pills.append({
                "category": "Digital Arrest / Isolation",
                "severity": "critical",
                "keywords": iso_matches,
                "score": 1.0
            })

        return feature_vector, pills
