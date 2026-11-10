"""
Quick Kannada scam detection test.
Run from project root: python test_kannada.py
"""
from backend.model_runner import engine

# --- TEST 1: SCAM --- contains exact keywords the model trained on
# Authority impersonation + arrest threat + AnyDesk + OTP demand
SCAM_TEXT = (
    "Namaskara sir, naanu Mumbai CBI officer Sharma maataduttidini. "
    "Nimma aadhar card mele drug parcel case registered aagide. "
    "Turita AnyDesk download maadi, nimage arrest warrant issue aaguttade. "
    "OTP share maadi, naavu verify maaduttevi."
)

# --- TEST 2: SAFE --- genuine delivery call, none of the scam keywords
SAFE_TEXT = (
    "Namaskara, naanu Swiggy delivery partner maataduttidini. "
    "Nimma order ready aagide. Neevu maneyalli idira? "
    "Delivery maadalu barbahudu. Address confirm maadi please."
)

SEP = "-" * 60

def run_test(label, text):
    r = engine.predict_turn(text, turn_index=1, prev_cumulative_risk=0.0)
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(SEP)
    print(f"  Text     : {text[:80]}...")
    print(f"  Tier     : {r['tier']}")
    print(f"  Risk     : {r['cumulative_risk']}  ({round(r['cumulative_risk']*100)}%)")
    print(f"  Intent P : {r['intent_prob']}")
    print(f"  Red Flags: {[p['category'] for p in r['pills']] or 'None'}")
    print(f"  Advice   : {r['advice'][:80]}")
    print(f"  Source   : {r['models_source']}")

run_test("SCAM  — CBI/AnyDesk/OTP (Trained Keywords)", SCAM_TEXT)
run_test("SAFE  — Swiggy Delivery (No Scam Keywords)", SAFE_TEXT)
print(f"\n{'='*60}\n")
