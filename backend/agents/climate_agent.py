import os
import sys
import random
from typing import Dict, Any, List

# Ensure relative imports work depending on execution context
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.weather_service import get_weather

def detect_climate_risks(weather_data: Dict[str, float]) -> List[str]:
    """
    Applies rule-based detection for climate risks based on current weather data.
    """
    risks = []
    temperature = weather_data.get("temperature", 0)
    humidity = weather_data.get("humidity", 0)
    rainfall = weather_data.get("rainfall", 0)
    wind_speed = weather_data.get("wind_speed", 0)

    # Flood Risk & Heavy Rain Warning handling
    if rainfall > 80:
        risks.append("Flood Risk")
    elif 50 <= rainfall <= 80:
        risks.append("Heavy Rain Warning")
    
    # Heat Wave Risk
    if temperature > 40:
        risks.append("Heat Wave Risk")
        
    # Drought Risk
    if humidity < 25 and rainfall < 10:
        risks.append("Drought Risk")
        
    # Strong Wind Warning
    if wind_speed > 15:
        risks.append("Strong Wind Warning")
        
    return risks

def generate_advisories(risks: List[str]) -> str:
    """
    Generates simple, farmer-friendly recommendations based on detected risks.
    Combines multiple advisories into one single string if multiple exist.
    """
    advisories = []
    
    for risk in risks:
        if risk == "Flood Risk":
            advisories.append("Heavy rainfall expected. Farmers should harvest mature crops early and avoid irrigation.")
        elif risk == "Heavy Rain Warning":
            advisories.append("Heavy rain expected. Avoid applying fertilizers and ensure proper drainage.")
        elif risk == "Heat Wave Risk":
            advisories.append("Extreme heat expected. Provide shade and increase irrigation.")
        elif risk == "Drought Risk":
            advisories.append("Low rainfall expected. Use water-saving irrigation methods.")
        elif risk == "Strong Wind Warning":
            advisories.append("Strong winds expected. Secure plants and protect fragile crops.")
            
    if not advisories:
        return "Weather conditions are optimal. Continue standard farming practices."
        
    return " ".join(advisories)

def analyze_climate(region: str) -> Dict[str, Any]:
    """
    Main orchestrator function for the Climate Agent.
    Workflow:
    1. Fetch weather data using weather_service
    2. Analyze climate risks
    3. Generate advisories
    4. Return structured response conforming to AgriSphere standard
    """
    weather_data = get_weather(region)
    risks = detect_climate_risks(weather_data)
    recommendation = generate_advisories(risks)
    
    # Return standard AgriSphere response format
    return {
        "agent": "climate_agent",
        "status": "ok",
        "data": {
            "region": region,
            "temperature": weather_data.get("temperature"),
            "humidity": weather_data.get("humidity"),
            "rainfall": weather_data.get("rainfall"),
            "wind_speed": weather_data.get("wind_speed"),
            "risks": risks
        },
        "recommendation": recommendation
    }

def climate_endpoint(region: str) -> Dict[str, Any]:
    """
    Helper function intended to be exposed as a FastAPI endpoint.
    Calls the analyze_climate function for the specified region.
    """
    return analyze_climate(region)

def simulate_region_climate() -> Dict[str, Any]:
    """
    Randomly generates weather conditions for demo purposes during a hackathon.
    Helps simulate different regions quickly.
    """
    demo_regions = [
        "Tamil Nadu", "Maharashtra", "Punjab", 
        "Kerala", "Assam", "Gujarat", "Karnataka"
    ]
    random_region = random.choice(demo_regions)
    
    # The analyze_climate function will fallback to simulate weather 
    # if the OpenWeather API key naturally isn't set, providing mock values
    # across the target temperature ranges.
    return analyze_climate(random_region)

if __name__ == "__main__":
    # Test execution for verification
    import json
    print("Testing standard climate analysis:")
    print(json.dumps(analyze_climate("Tamil Nadu"), indent=2))
    
    print("\nTesting remote simulation function:")
    print(json.dumps(simulate_region_climate(), indent=2))
