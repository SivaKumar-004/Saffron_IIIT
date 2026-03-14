from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from agents.main_agent import MainAgent

app = FastAPI(title="AgriSphere API")
main_agent = MainAgent()

class AskRequest(BaseModel):
    query_type: str
    payload: Optional[dict] = {}

class ClimateRequest(BaseModel):
    region: str

class PlantRequest(BaseModel):
    plant_name: str

@app.post("/ask-agrisphere")
def ask_agrisphere(request: AskRequest):
    return main_agent.process_query(request.query_type, request.payload)

@app.post("/climate")
def ask_climate(request: ClimateRequest):
    return main_agent.process_query("climate", {"region": request.region})

@app.post("/farm")
def ask_farm():
    return main_agent.process_query("farm", {})

@app.post("/plant")
def ask_plant(request: PlantRequest):
    return main_agent.process_query("plant", {"plant_name": request.plant_name})
