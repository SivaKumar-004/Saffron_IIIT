# Climate Intelligence Agent

def analyze_climate(region: str) -> dict:
    """
    Analyzes climate conditions and provides risk assessments.
    """
    # SECURITY: Sanitize input region
    region = str(region)[:50].strip() if region else "General"
    # Simulated metrics (would be real API in production)
    temperature = 42.0
    humidity = 18.0
    rainfall = 85.0
    
    risk = "Normal"
    recommendations = []

    if rainfall > 80.0:
        risk = "Flood Risk"
        recommendations.append("Heavy rainfall expected. Harvest crops early.")
    elif temperature > 40.0:
        risk = "Heat Wave"
        recommendations.append("Extreme heat expected. Increase irrigation.")
    elif humidity < 20.0:
        risk = "Drought Risk"
        recommendations.append("Low humidity detected. Increase watering frequency.")
    else:
        recommendations.append("Climate conditions are favorable.")

    return {
        "agent": "climate_agent",
        "status": "ok",
        "data": {
            "temperature": f"{temperature}°C",
            "rainfall": f"{rainfall}mm",
            "humidity": f"{humidity}%",
            "risk": risk
        },
        "recommendation": " ".join(recommendations)
    }
