"""
Precision Agriculture Sensor Agent for AgriSphere.

This module simulates farm sensor data, analyzes it, and returns
irrigation recommendations in a standard response format.
"""

import random
from typing import Dict, Any, Union

def simulate_sensor_data() -> Dict[str, Union[int, float, str]]:
    """
    Simulate sensor data with realistic random values.

    Returns:
        dict: Simulated sensor metrics including soil_moisture,
              soil_temperature, humidity, and light_intensity.
    """
    # Simulate specific fields with provided ranges
    soil_moisture = random.randint(10, 60)
    soil_temperature = round(random.uniform(20.0, 40.0), 2)
    humidity = random.randint(30, 80)
    
    # Map a random integer to a light intensity category
    lux_value = random.randint(0, 1000)
    if lux_value < 300:
        light_intensity = "low"
    elif lux_value <= 700:
        light_intensity = "medium"
    else:
        light_intensity = "high"
        
    return {
        "soil_moisture": soil_moisture,
        "soil_temperature": soil_temperature,
        "humidity": humidity,
        "light_intensity": light_intensity
    }

def recommend_irrigation(soil_moisture: int) -> str:
    """
    Determine irrigation recommendation based on soil moisture levels.

    Args:
        soil_moisture (int): The current soil moisture percentage.

    Returns:
        str: An irrigation recommendation string.
    """
    if soil_moisture < 30:
        return "Irrigation required today"
    elif 30 <= soil_moisture <= 50:
        return "Monitor soil moisture"
    else:
        return "No irrigation needed"

def analyze_farm() -> Dict[str, Any]:
    """
    Simulate farm data, analyze it, and provide a standardized response.

    Returns:
        dict: A dictionary matching the shared agent response format containing
              agent name, status, data, and recommendations. If an error occurs,
              an error variant is returned.
    """
    try:
        # Simulate the sensor readings
        sensor_data = simulate_sensor_data()
        
        # Determine recommendation based on soil moisture
        soil_moisture = sensor_data["soil_moisture"]
        recommendation = recommend_irrigation(soil_moisture)
        
        # Build the successful response payload
        return {
            "agent": "sensor_agent",
            "status": "ok",
            "data": sensor_data,
            "recommendation": recommendation
        }
    except Exception:
        # Handle unexpected errors and return a safe fallback response
        return {
            "agent": "sensor_agent",
            "status": "error",
            "data": {},
            "recommendation": "Unable to analyze farm data at this time."
        }

if __name__ == "__main__":
    # Example usage for testing
    result = analyze_farm()
    print("Sensor Agent Output:")
    import json
    print(json.dumps(result, indent=4))
