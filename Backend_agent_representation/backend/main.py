import asyncio
import os
import sys
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

# Setup logging for security monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgriSphereSecurity")

# Ensure the agents module can be imported properly
sys.path.append(os.path.dirname(__file__))
from agents.sensor_agent import analyze_farm
from agents.climate_agent import analyze_climate
from agents.plant_agent import analyze_plant

app = FastAPI(title="AgriSphere Multi-Agent API (Hardened)")

# SECURITY: Restrict CORS to local development environment
# Prevents unauthorized domains from making requests to the API
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# SECURITY: Strict Input Validation Models
class PlantPayload(BaseModel):
    plant_name: str = Field(..., max_length=50, pattern="^[a-zA-Z ]+$")
    soil_moisture: float = Field(default=40.0, ge=0, le=100)
    light_level: str = Field(default="medium", pattern="^(low|medium|high)$")
    temperature: float = Field(default=22.0, ge=-50, le=100)

class AgentRequest(BaseModel):
    query_type: str = Field(..., pattern="^(climate|sensor|plant)$")
    payload: Optional[dict] = {}

@app.get("/health")
def health_check():
    return {"status": "AgriSphere Master Backend is Online", "security": "Hardened"}

@app.post("/ask-agent")
async def ask_agent(request: AgentRequest):
    """Directly query a specific agent with validated input."""
    try:
        if request.query_type == "climate":
            # SECURITY: Handle empty/None payload safely
            payload = request.payload or {}
            region = str(payload.get("region", "General"))[:50] 
            return analyze_climate(region)
        
        elif request.query_type == "sensor":
            return analyze_farm()
        
        elif request.query_type == "plant":
            # Extra validation for plant payload
            p = PlantPayload(**request.payload)
            return analyze_plant(p.plant_name, p.soil_moisture, p.light_level, p.temperature)
            
    except Exception as e:
        logger.error(f"Security/Validation Error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid request parameters")

@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """
    WebSocket that streams a consolidated view of ALL agents.
    Includes robust error isolation.
    """
    await websocket.accept()
    logger.info("New WebSocket connection established.")
    try:
        while True:
            try:
                # Gather data from all agents
                sensor_results = analyze_farm()
                climate_results = analyze_climate("Main Sector")
                
                # Use real sensor data to feed the plant agent logic
                plant_results = analyze_plant(
                    "tomato", 
                    sensor_results['data'].get('soil_moisture', 40),
                    sensor_results['data'].get('light_intensity', 'medium'),
                    sensor_results['data'].get('soil_temperature', 22)
                )

                payload = {
                    "timestamp": asyncio.get_event_loop().time(),
                    "sensor": sensor_results,
                    "climate": climate_results,
                    "plant": plant_results
                }
                
                await websocket.send_json(payload)
            except Exception as e:
                logger.error(f"Internal Agent Stream Error: {e}")
            
            await asyncio.sleep(3) 
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")
    except Exception as e:
        logger.fatal(f"WebSocket Critical Failure: {e}")
        await websocket.close()

# Mount frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
