from .climate_agent import analyze_climate
from .sensor_agent import analyze_farm
from .plant_agent import analyze_plant

class MainAgent:
    def process_query(self, query_type: str, payload: dict) -> dict:
        """
        Routes the request to the appropriate sub-agent based on query_type.
        """
        if query_type == "climate":
            region = payload.get("region", "unknown")
            return analyze_climate(region)
            
        elif query_type == "farm":
            return analyze_farm()
            
        elif query_type == "plant":
            plant_name = payload.get("plant_name", "unknown")
            return analyze_plant(plant_name)
            
        else:
            return {
                "agent": "main_agent",
                "status": "error",
                "data": {},
                "recommendation": "Unknown query type."
            }
