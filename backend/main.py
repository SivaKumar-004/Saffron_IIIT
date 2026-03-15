import asyncio
import os
import sys
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.dirname(__file__))
from agents.sensor_agent import analyze_farm
from agents.crew_orchestrator import run_tier2_crew
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AgriSphere Real-Time API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FarmState:
    anomaly_active = False
    latest_agent_insight = "Monitoring nominal conditions."

@app.post("/api/inject-anomaly")
async def trigger_anomaly():
    FarmState.anomaly_active = True
    return {"status": "Critical drought anomaly injected. Agents are analyzing..."}

@app.websocket("/ws/sensor-data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to sensor-data websocket.")
    try:
        while True:
            payload = analyze_farm()
            
            if FarmState.anomaly_active:
                payload["data"]["soil_moisture"] = "12.0"  # Critical
                payload["data"]["soil_temperature"] = "35.5" # Hot
                
                print("Anomaly detected! Waking up CrewAI...")
                
                # Sync call for hackathon simplicity
                agent_report = run_tier2_crew(payload["data"], anomaly_detected=True)
                FarmState.latest_agent_insight = agent_report
                FarmState.anomaly_active = False
                
            payload["agent_insight"] = FarmState.latest_agent_insight
            await websocket.send_json(payload)
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"WebSocket Error: {e}")

frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print(f"Warning: Frontend dashboard not found at {frontend_path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
