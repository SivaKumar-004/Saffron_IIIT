# MEMBER 3 - Tier 2 - Precision Farm Sensor Agent

import random

def analyze_farm() -> dict:
    # 1. Provide a sensor simulator function that generates random values.
    soil_moisture = random.uniform(10, 60)
    temperature = random.uniform(20, 40)
    humidity = random.uniform(30, 80)

    recommendations = []

    # 2. Implement irrigation recommendation logic.
    if soil_moisture < 30:
        recommendations.append("Irrigation required today.")
    elif soil_moisture > 50:
        recommendations.append("No irrigation needed.")
    else:
        recommendations.append("Soil moisture is adequate.")

    final_recommendation = " ".join(recommendations)

    # 3. Return results in the shared response format
    return {
        "agent": "sensor_agent",
        "status": "ok",
        "data": {
            "soil_moisture": f"{soil_moisture:.1f}",
            "temperature": f"{temperature:.1f}",
            "humidity": f"{humidity:.1f}"
        },
        "recommendation": final_recommendation
    }
