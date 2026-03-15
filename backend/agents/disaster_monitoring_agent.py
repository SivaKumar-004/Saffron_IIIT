import os
import sys
from typing import Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.weather_service import get_weather

class DisasterMonitoringAgent:
    """
    Tier 1 Agent: Disaster Monitoring Agent
    Responsibility: Ingests weather and disaster APIs to collect necessary data.
    """
    def __init__(self):
        self.name = "Disaster Monitoring Agent"

    def monitor_region(self, region: str) -> Dict[str, Any]:
        """
        Fetches the primary data payload for the requested region.
        """
        # We leverage the existing reliable weather extraction service
        weather_data = get_weather(region)
        
        return {
            "region": region,
            "metrics": weather_data
        }

# Example usage
if __name__ == "__main__":
    agent = DisasterMonitoringAgent()
    print(agent.monitor_region("Tamil Nadu"))
