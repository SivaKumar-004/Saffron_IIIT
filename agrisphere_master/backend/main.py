from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import time

# Import agents as specified
from backend.agents.main_agent import route_query
from backend.agents.climate_agent import analyze_climate, simulate_climate_demo
from backend.agents.sensor_agent import analyze_farm
from backend.agents.plant_agent import analyze_plant
from backend.agents.call_orchestrator import FarmerCallOrchestrator

call_agent = FarmerCallOrchestrator()

app = FastAPI(title="AgriSphere API", description="Integrated Multi-Agent Agricultural platform")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared state for background task demo
shared_telemetry = {
    "last_sync": 0,
    "status": "initializing"
}

# Request Models
class ClimateRequest(BaseModel):
    region: str

class PlantRequest(BaseModel):
    plant_name: str

class CallRequest(BaseModel):
    transcript: str

class GenericRequest(BaseModel):
    query_type: str
    region: str | None = None
    plant_name: str | None = None
    soil_moisture: float | None = None

# Error response helper
def error_response(msg: str):
    return {
        "agent": "system",
        "status": "error",
        "data": {},
        "recommendation": msg
    }

@app.get("/")
def read_root():
    return {"status": "AgriSphere Integrated Backend is Online", "telemetry": shared_telemetry}

@app.post("/climate")
def handle_climate(request: ClimateRequest):
    if not request.region:
        return error_response("Invalid request parameters: 'region' is required.")
    return analyze_climate(request.region)

@app.get("/api/climate")
def api_climate(region: str):
    if not region:
        return error_response("Invalid request parameters: 'region' is required.")
    return analyze_climate(region)

@app.get("/api/climate/simulate")
def api_climate_simulate():
    return simulate_climate_demo()

@app.post("/api/call")
def api_call(req: CallRequest):
    try:
        reply = call_agent.process_call(req.transcript)
        return reply
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/farm")
def handle_farm():
    # No required input per specs
    return analyze_farm()

@app.post("/plant")
def handle_plant(request: PlantRequest):
    if not request.plant_name:
        return error_response("Invalid request parameters: 'plant_name' is required.")
    return analyze_plant(request.plant_name)

@app.post("/ask-agrisphere")
def handle_ask_agrisphere(request: GenericRequest):
    """
    Main AI endpoint with routing logic.
    """
    if request.query_type == "climate":
        if not request.region:
            return error_response("Invalid request parameters")
        return analyze_climate(request.region)

    if request.query_type == "farm":
        return analyze_farm()

    if request.query_type == "plant":
        if not request.plant_name:
            return error_response("Invalid request parameters")
        
        moisture = request.soil_moisture if request.soil_moisture is not None else 40.0
        return analyze_plant(request.plant_name, moisture)
    
    return error_response("Unknown query type")

# Optional Demo Feature: Background Telemetry Simulation
async def simulate_sensors():
    while True:
        shared_telemetry["last_sync"] = time.time()
        shared_telemetry["status"] = "active"
        # In a real app, this might update a database or cache
        await asyncio.sleep(5)

# --- MASTER ORCHESTRATOR CHATBOT LOGIC ---

from fastapi import WebSocket, WebSocketDisconnect
import json
import os
import google.generativeai as genai

# Async wrappers for the blocking sub-agent calls
async def async_analyze_climate(region: str):
    try:
        return await asyncio.to_thread(analyze_climate, region)
    except Exception as e:
        return {"agent": "climate_agent", "status": "error", "error": str(e), "recommendation": "Climate data unavailable."}

async def async_analyze_farm():
    try:
        return await asyncio.to_thread(analyze_farm)
    except Exception as e:
        return {"agent": "sensor_agent", "status": "error", "error": str(e), "recommendation": "Farm sensor data unavailable."}

async def async_analyze_plant(plant_name: str, moisture: float = 40.0):
    try:
        # In this implementation, the backend handles passing the moisture from the farm directly to the plant
        return await asyncio.to_thread(analyze_plant, plant_name, moisture, "medium", 22.0)
    except Exception as e:
        return {"agent": "plant_agent", "status": "error", "error": str(e), "recommendation": "Plant intelligence unavailable."}

@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """
    WebSocket that streams a consolidated view of ALL agents.
    Provides live telemetry for the Tier 2 Advanced Farm Dashboard.
    """
    await websocket.accept()
    
    state = {"crop": "tomato"}
    
    async def receive_loop():
        try:
            while True:
                data = await websocket.receive_text()
                parsed = json.loads(data)
                if parsed.get("type") == "set_crop":
                    state["crop"] = parsed.get("crop", "tomato")
        except Exception:
            pass
            
    async def send_loop():
        try:
            while True:
                # Gather data concurrently from all agents
                sensor_task = asyncio.create_task(async_analyze_farm())
                climate_task = asyncio.create_task(async_analyze_climate("Tamil Nadu"))
                
                sensor_res, climate_res = await asyncio.gather(sensor_task, climate_task, return_exceptions=True)
                
                # Default safety fallbacks
                sensor_data = sensor_res if not isinstance(sensor_res, Exception) else {"status": "error", "data": {"soil_moisture": 40, "soil_temperature": 22, "humidity": 50}, "recommendation": "Sensor offline"}
                climate_data = climate_res if not isinstance(climate_res, Exception) else {"status": "error", "data": {"risk": "Unknown", "rainfall": "0mm"}, "recommendation": "Climate offline"}
                
                moisture_val = sensor_data.get('data', {}).get('soil_moisture', 40.0)
                
                # Plant intelligence driven by mock sensor
                plant_res = await async_analyze_plant(state["crop"], float(moisture_val))
                plant_data = plant_res if not isinstance(plant_res, Exception) else {"status": "error", "recommendation": "Plant logic offline"}

                payload = {
                    "timestamp": time.time(),
                    "sensor": sensor_data,
                    "climate": climate_data,
                    "plant": plant_data
                }
                
                await websocket.send_text(json.dumps(payload))
                await asyncio.sleep(3) 
        except Exception as e:
            print(f"Internal Dashboard Stream Error: {e}")

    rcvr = asyncio.create_task(receive_loop())
    sndr = asyncio.create_task(send_loop())
    
    try:
        done, pending = await asyncio.wait([rcvr, sndr], return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
    except WebSocketDisconnect:
        print("Dashboard WebSocket disconnected.")
        for task in [rcvr, sndr]: task.cancel()
    except Exception as e:
        print(f"WebSocket Critical Failure: {e}")
        await websocket.close()

@app.websocket("/ws/master-chat")
async def master_chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Initialize Gemini for powerful response synthesis
    api_key = os.getenv("GEMINI_API_KEY")
    synthesis_model = None
    if api_key:
        try:
            genai.configure(api_key=api_key.strip())
            synthesis_model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception:
            pass # Fallback to basic string processing if key is invalid

    await websocket.send_text(json.dumps({
        "sender": "bot",
        "message": "Hello! I am the AgriSphere Master Orchestrator. Ask me about your farm sensors, climate risks, or plant care."
    }))

    try:
        while True:
            data = await websocket.receive_text()
            user_query = data.lower()
            
            # Simple keyword-based natural language routing
            needs_climate = any(kw in user_query for kw in ["weather", "climate", "rain", "temperature", "heat", "flood", "wind", "safe", "forecast", "risk"])
            needs_farm    = any(kw in user_query for kw in ["sensor", "farm", "moisture", "dry", "wet", "soil", "irrigation", "water", "safe"])
            needs_plant   = any(kw in user_query for kw in ["plant", "crop", "tomato", "basil", "carrot", "lettuce", "grow", "safe", "companion"])
            
            # Identify specific parameters from the query
            target_region = "Tamil Nadu" if "tamil nadu" in user_query else "Default Region"
            target_plant = "tomato" # Default
            for plant in ["tomato", "carrot", "basil", "lettuce", "pepper", "potato"]:
                if plant in user_query:
                    target_plant = plant
                    break

            await websocket.send_text(json.dumps({"sender": "bot", "message": "Analyzing across the AgriSphere tiers..."}))

            # Fire off required agents concurrently (Cross-Tier Intelligence)
            tasks = []
            if needs_climate:
                tasks.append(asyncio.create_task(async_analyze_climate(target_region), name="climate"))
            if needs_farm:
                tasks.append(asyncio.create_task(async_analyze_farm(), name="farm"))
            
            # Wait for first tier telemetry if plant agent needs it
            farm_result = None
            task_results = {}
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for task, result in zip(tasks, results):
                    task_name = task.get_name()
                    task_results[task_name] = result
                    if task_name == "farm" and not isinstance(result, Exception):
                        farm_result = result
            
            if needs_plant:
                moisture_val = 40.0
                if farm_result and farm_result.get("status") == "ok":
                    try:
                        moisture_val = float(farm_result["data"]["soil_moisture"])
                    except:
                        pass
                
                # Fetch plant data now that we have farm telemetry
                plant_res = await async_analyze_plant(target_plant, moisture_val)
                task_results["plant_res"] = plant_res

            # Synthesize Context
            context_string = ""
            if "climate" in task_results:
                 c_res = task_results["climate"]
                 if not isinstance(c_res, Exception) and c_res.get("status") == "ok":
                     context_string += f"Climate Data ({c_res['data']['region']}): {c_res['data']['temperature']}C, Risks: {', '.join(c_res['data']['risks']) if c_res['data']['risks'] else 'None'}. Advisory: {c_res['recommendation']}\n"
                 else:
                     context_string += "Climate Agent: Offline/Error.\n"
            
            if "farm" in task_results:
                 f_res = task_results["farm"]
                 if not isinstance(f_res, Exception) and f_res.get("status") == "ok":
                     context_string += f"Farm Sensors: Soil Moisture {f_res['data']['soil_moisture']}%, Temp {f_res['data']['temperature']}C. Advice: {f_res['recommendation']}\n"
                 else:
                     context_string += "Farm Agent: Offline/Error.\n"
                     
            if "plant_res" in task_results:
                 p_res = task_results["plant_res"]
                 if not isinstance(p_res, Exception) and p_res.get("status") == "ok":
                     context_string += f"Plant Expert ({target_plant}): {p_res['recommendation']}\n"
                 else:
                     context_string += "Plant Agent: Offline/Error.\n"

            if not context_string:
                 await websocket.send_text(json.dumps({
                    "sender": "bot",
                    "message": "I couldn't identify which sub-systems to query based on your question. Try asking about weather, soil moisture, or specific crops like tomatoes."
                }))
                 continue

            # Produce Final Synthesized Answer
            final_answer = ""
            if synthesis_model:
                prompt = (
                    f"You are the AgriSphere Master Agent Chatbot answering a farmer.\n"
                    f"User asked: '{user_query}'\n"
                    f"Here is the raw data from your sub-agents:\n{context_string}\n"
                    f"Write a friendly, concise, and helpful response synthesizing this data to directly answer their question. Keep it under 4 sentences."
                )
                try:
                    ai_response = synthesis_model.generate_content(prompt)
                    final_answer = ai_response.text
                except Exception as e:
                     final_answer = "Error synthesizing with LLM: " + str(e) + "\n\nRaw Data:\n" + context_string
            else:
                # Basic string concatenation fallback if no API key
                final_answer = f"Here is the data from across the platform:\n\n{context_string}"

            # Stream result back
            await websocket.send_text(json.dumps({
                "sender": "bot",
                "message": final_answer
            }))

    except WebSocketDisconnect:
        print("Master Chat disconnected")


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulate_sensors())
