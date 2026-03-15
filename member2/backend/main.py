from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Import our Tier 1 multi-agent orchestrator
from agents.tier1_orchestrator import orchestrate_climate, simulate_tier1_region
from agents.call_orchestrator import FarmerCallOrchestrator
from pydantic import BaseModel

# Initialize the Call Agent single instance
call_agent = FarmerCallOrchestrator()

class CallRequest(BaseModel):
    transcript: str

app = FastAPI(
    title="AgriSphere Backend API",
    description="Backend services for the AgriSphere AI-driven agriculture system.",
    version="1.0.0"
)

# Configure CORS so the frontend can easily communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AgriSphere API."}

@app.get("/api/climate")
def get_climate_analysis(region: str = Query(..., description="The region or city to analyze.")):
    """
    Tier 1 – Rural Climate & Disaster Intelligence Endpoint.
    Executes the Disaster Monitoring, Climate Prediction, and Farmer Alert agents.
    """
    try:
        result = orchestrate_climate(region)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/climate/simulate")
def get_climate_simulation():
    """
    Hackathon Demo Endpoint.
    Randomly generates weather conditions for different regions to simulate full pipeline.
    """
    try:
        result = simulate_tier1_region()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/call")
def simulate_farmer_call(req: CallRequest):
    """
    Endpoint for a simulated natural-language call from a farmer to register details.
    """
    try:
        reply = call_agent.process_call(req.transcript)
        return reply
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
