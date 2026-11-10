from typing import List, Dict, Any

SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "scenario_digital_arrest",
        "title": "🚨 Digital Arrest (Mumbai Police & Drugs Parcel)",
        "language": "Kannada + English (Kanglish)",
        "description": "Scammer impersonates Mumbai Police/CBI, claims an Aadhaar drug parcel was seized, and demands isolation & money.",
        "turns": [
            {
                "turn": 1,
                "text_kannada": "Namaskara sir, naavu Mumbai Crime Branch police station inda call maadtidivi.",
                "text_english": "Hello sir, we are calling from Mumbai Crime Branch police station.",
                "pause_sec": 3.0
            },
            {
                "turn": 2,
                "text_kannada": "Nimma Aadhaar card number mele illegal FedEx parcel seize aagide, athralli MDMA drugs ide.",
                "text_english": "An illegal FedEx parcel registered under your Aadhaar card has been seized, containing MDMA drugs.",
                "pause_sec": 3.5
            },
            {
                "turn": 3,
                "text_kannada": "CBI inda non-bailable arrest warrant issue aagide sir, call disconnect maadbedi.",
                "text_english": "A non-bailable arrest warrant has been issued by CBI sir, do not disconnect this call.",
                "pause_sec": 4.0
            },
            {
                "turn": 4,
                "text_kannada": "Neevu eegle private room ge hogi, Skype video call open maadi digital arrest procedure complete maadi.",
                "text_english": "Go to a private room immediately, open Skype video call, and complete the digital arrest procedure.",
                "pause_sec": 4.5
            },
            {
                "turn": 5,
                "text_kannada": "Warrant cancel aagbekandre, RBI safe custody account ge 50,000 security deposit eegle transfer maadi.",
                "text_english": "To cancel the warrant, transfer 50,000 rupees security deposit to RBI safe custody account immediately.",
                "pause_sec": 4.0
            }
        ]
    },
    {
        "id": "scenario_bescom_bill",
        "title": "⚡ BESCOM Electricity Bill Cut Scam",
        "language": "Kannada + English",
        "description": "Scammer threatens immediate residential power disconnection unless an APK app is installed or bill is re-paid.",
        "turns": [
            {
                "turn": 1,
                "text_kannada": "Dear consumer, BESCOM electricity power department inda alert message.",
                "text_english": "Dear consumer, alert notification from BESCOM electricity power department.",
                "pause_sec": 3.0
            },
            {
                "turn": 2,
                "text_kannada": "Nimma last month electricity bill payment portal alli update aagilla.",
                "text_english": "Your last month electricity bill payment has not been updated in the portal.",
                "pause_sec": 3.5
            },
            {
                "turn": 3,
                "text_kannada": "Tonight at 8 PM nimma power supply line permanently cut aagatte.",
                "text_english": "Tonight at 8 PM your residential power supply line will be permanently disconnected.",
                "pause_sec": 4.0
            },
            {
                "turn": 4,
                "text_kannada": "Disconnection stop maadbekandre, BESCOM support APK download maadi bill verify maadi.",
                "text_english": "To stop power disconnection, download our BESCOM support APK app and verify your bill.",
                "pause_sec": 4.5
            },
            {
                "turn": 5,
                "text_kannada": "Mobile ge bandiro 6-digit OTP share maadi, urgent aagi verify aagatte.",
                "text_english": "Share the 6-digit OTP received on your mobile, it will be verified urgently.",
                "pause_sec": 4.0
            }
        ]
    },
    {
        "id": "scenario_anydesk_sim",
        "title": "📲 TRAI SIM Deactivation & AnyDesk Fraud",
        "language": "English + Hindi/Kanglish",
        "description": "Scammer claims telecom SIM will be blocked within 2 hours, forcing remote access app installation.",
        "turns": [
            {
                "turn": 1,
                "text_kannada": "Hello sir, calling from Telecom Regulatory Authority of India TRAI verification desk.",
                "text_english": "Hello sir, calling from Telecom Regulatory Authority of India TRAI verification desk.",
                "pause_sec": 3.0
            },
            {
                "turn": 2,
                "text_kannada": "Your mobile SIM card is involved in illegal SMS spamming, and will be deactivated in 2 hours.",
                "text_english": "Your mobile SIM card is involved in illegal SMS spamming, and will be deactivated in 2 hours.",
                "pause_sec": 3.5
            },
            {
                "turn": 3,
                "text_kannada": "To avoid permanent SIM block, open Google Play Store right now.",
                "text_english": "To avoid permanent SIM block, open Google Play Store right now.",
                "pause_sec": 3.5
            },
            {
                "turn": 4,
                "text_kannada": "Search and install AnyDesk or QuickSupport application for remote KYC verification.",
                "text_english": "Search and install AnyDesk or QuickSupport application for remote KYC verification.",
                "pause_sec": 4.0
            },
            {
                "turn": 5,
                "text_kannada": "Read out the 9-digit address code and enter your UPI PIN to approve the test transaction.",
                "text_english": "Read out the 9-digit address code and enter your UPI PIN to approve the test transaction.",
                "pause_sec": 4.0
            }
        ]
    },
    {
        "id": "scenario_genuine_delivery",
        "title": "🛵 Genuine Delivery & Routine Bank Inquiry (HAM / Safe)",
        "language": "Kannada + English",
        "description": "Normal delivery partner call and safe customer service inquiry with zero red flags.",
        "turns": [
            {
                "turn": 1,
                "text_kannada": "Namaskara sir, naanu Swiggy delivery partner, apartment gate hatthira idini.",
                "text_english": "Hello sir, I am Swiggy delivery partner, I am near the apartment main gate.",
                "pause_sec": 3.0
            },
            {
                "turn": 2,
                "text_kannada": "Security guard entry code kelthidare, entry approve maadi sir.",
                "text_english": "Security guard is asking for entry code, please approve entry on your app sir.",
                "pause_sec": 3.5
            },
            {
                "turn": 3,
                "text_kannada": "Okay sir, lift alli 4th floor flat 402 ge bartidini.",
                "text_english": "Okay sir, taking the lift to 4th floor flat 402 right away.",
                "pause_sec": 3.0
            },
            {
                "turn": 4,
                "text_kannada": "Here is your food package sir, seal check maadi.",
                "text_english": "Here is your food package sir, please check if seal is intact.",
                "pause_sec": 3.0
            },
            {
                "turn": 5,
                "text_kannada": "Thank you sir, app alli rating kodi, have a nice day!",
                "text_english": "Thank you sir, please provide rating on the app, have a nice day!",
                "pause_sec": 3.0
            }
        ]
    }
]
