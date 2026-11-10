import uvicorn
import os
import sys

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print("\n" + "="*60)
    print("RAKSHAK-AI: GNANI REAL-TIME SCAM SHIELD DASHBOARD")
    print("="*60)
    print(f"Server URL: http://localhost:{port}")
    print(f"WebSocket Audio Stream: ws://localhost:{port}/ws/stream-audio")
    print(f"Simulation Stream: ws://localhost:{port}/ws/simulation")
    print("="*60 + "\n")
    uvicorn.run("backend.app:app", host="0.0.0.0", port=port, reload=True)
