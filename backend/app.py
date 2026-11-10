import os
import json
import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

from backend.config import FRONTEND_DIR, GNANI_API_KEY
from backend.model_runner import engine
from backend.sample_scenarios import SCENARIOS
from backend.gnani_client import GnaniStreamingClient

logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Gnani Kanglish Real-Time Scam Detection Shield")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextAnalysisRequest(BaseModel):
    text: str
    turn_index: Optional[int] = 1
    prev_cumulative_risk: Optional[float] = 0.0
    dialogue_history: Optional[List[str]] = None

@app.get("/api/status")
async def get_status():
    """Returns engine health and model status."""
    return {
        "status": "online",
        "gnani_configured": bool(GNANI_API_KEY),
        "trained_models_loaded": engine.trained_models_loaded,
        "engine_mode": "colab_trained" if engine.trained_models_loaded else "smart_stacking_engine",
        "supported_languages": ["Kannada (kn-IN)", "Kanglish (Code-mixed)", "English"]
    }

@app.get("/api/scenarios")
async def get_scenarios():
    """Returns list of interactive telephony demonstration scenarios."""
    return SCENARIOS

@app.post("/api/analyze-turn")
async def analyze_turn(payload: TextAnalysisRequest):
    """Direct REST endpoint to evaluate a single turn text."""
    result = engine.predict_turn(
        text=payload.text,
        turn_index=payload.turn_index,
        prev_cumulative_risk=payload.prev_cumulative_risk,
        dialogue_history=payload.dialogue_history
    )
    return result

@app.websocket("/ws/simulation")
async def websocket_simulation(websocket: WebSocket):
    """
    Simulates a live phone call scenario turn-by-turn.
    Demonstrates the 1-minute 3-tier progressive decision horizon in real time!
    """
    await websocket.accept()
    logger.info("Client connected to Simulation WebSocket.")
    cumulative_risk = 0.0
    history = []

    try:
        # Client sends scenario_id to trigger
        init_data = await websocket.receive_text()
        req = json.loads(init_data)
        scenario_id = req.get("scenario_id", "scenario_digital_arrest")

        target_scenario = next((s for s in SCENARIOS if s["id"] == scenario_id), SCENARIOS[0])
        logger.info(f"Starting simulation: {target_scenario['title']}")

        await websocket.send_json({
            "type": "scenario_start",
            "scenario": {
                "id": target_scenario["id"],
                "title": target_scenario["title"],
                "language": target_scenario["language"],
                "total_turns": len(target_scenario["turns"])
            }
        })

        for turn_data in target_scenario["turns"]:
            # Realistic pause simulating telephone speech
            pause_time = float(turn_data.get("pause_sec", 3.0))
            await asyncio.sleep(pause_time)

            turn_num = turn_data["turn"]
            kannada_text = turn_data["text_kannada"]
            english_text = turn_data["text_english"]

            # Analyze the turn (combining English semantic analysis + Kannada trigger markers)
            eval_text = f"{english_text} {kannada_text}"
            res = engine.predict_turn(
                text=eval_text,
                turn_index=turn_num,
                prev_cumulative_risk=cumulative_risk,
                dialogue_history=history
            )

            cumulative_risk = res["cumulative_risk"]
            history.append(english_text)

            # Send rich real-time update to web dashboard
            await websocket.send_json({
                "type": "turn_update",
                "turn": turn_num,
                "text_kannada": kannada_text,
                "text_english": english_text,
                "intent_prob": res["intent_prob"],
                "turn_risk": res["turn_risk"],
                "cumulative_risk": res["cumulative_risk"],
                "tier": res["tier"],
                "tier_label": res["tier_label"],
                "status_color": res["status_color"],
                "pills": res["pills"],
                "advice": res["advice"]
            })

        await websocket.send_json({"type": "scenario_complete", "final_risk": cumulative_risk})

    except WebSocketDisconnect:
        logger.info("Simulation WebSocket disconnected.")
    except Exception as e:
        logger.error(f"Error in simulation WebSocket: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass

@app.websocket("/ws/stream-audio")
async def websocket_stream_audio(websocket: WebSocket):
    """
    Ingests live 16-bit 16kHz PCM audio stream from browser microphone.
    Relays audio to Gnani STT WebSocket and analyzes completed turns.
    """
    await websocket.accept()
    logger.info("Client connected to Live Audio WebSocket.")
    gnani = GnaniStreamingClient()
    connected_gnani = await gnani.connect()

    cumulative_risk = 0.0
    turn_index = 1
    history = []

    try:
        while True:
            # Receive binary audio chunk or control JSON
            message = await websocket.receive()
            if "bytes" in message:
                pcm_data = message["bytes"]
                if connected_gnani:
                    await gnani.stream_audio_chunk(pcm_data)
            elif "text" in message:
                ctrl = json.loads(message["text"])
                # If client sends manual transcription turn
                if ctrl.get("type") == "transcript_turn":
                    text = ctrl.get("text", "")
                    if text.strip():
                        res = engine.predict_turn(
                            text=text,
                            turn_index=turn_index,
                            prev_cumulative_risk=cumulative_risk,
                            dialogue_history=history
                        )
                        cumulative_risk = res["cumulative_risk"]
                        history.append(text)
                        turn_index += 1

                        await websocket.send_json({
                            "type": "turn_update",
                            "turn": res["turn_index"],
                            "text": text,
                            "cumulative_risk": res["cumulative_risk"],
                            "tier": res["tier"],
                            "tier_label": res["tier_label"],
                            "status_color": res["status_color"],
                            "pills": res["pills"],
                            "advice": res["advice"]
                        })

    except WebSocketDisconnect:
        logger.info("Audio WebSocket disconnected.")
    finally:
        await gnani.close()

# Serve frontend — StaticFiles mount handles /, /style.css, /app.js etc.
# No explicit FileResponse routes needed (they would conflict with the mount).
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
