# MEMBER 1 - Main Agent Orchestrator

from backend.agents.climate_agent import analyze_climate
from backend.agents.sensor_agent import analyze_farm
from backend.agents.plant_agent import analyze_plant

def route_query(query_type: str, payload: dict) -> dict:
    """
    Acts as an orchestrator. Route requests to appropriate sub-agents.
    """
    query_type = query_type.lower().strip()
    
    if query_type == "climate":
        region = payload.get("region", "Farm Sector Alpha")
        return analyze_climate(region)
        
    elif query_type == "farm":
        return analyze_farm()
        
    elif query_type == "plant":
        plant_name = payload.get("plant_name", "unknown")
        soil_moisture = payload.get("soil_moisture", 40.0)
        light_level = payload.get("light_level", "medium")
        temperature = payload.get("temperature", 22.0)
        return analyze_plant(plant_name, soil_moisture, light_level, temperature)
        
    else:
        return {
            "agent": "main_agent",
            "status": "error",
            "data": {},
            "recommendation": f"Unknown query type: {query_type}. Supported types: climate, farm, plant."
        }
