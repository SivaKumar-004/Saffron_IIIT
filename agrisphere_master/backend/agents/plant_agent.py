# Plant compatibility database
COMPATIBLE_PLANTS = {
    "tomato": ["basil", "marigold", "onion"],
    "carrot": ["lettuce", "radish", "pea"],
    "basil": ["tomato", "pepper", "oregano"],
    "lettuce": ["carrot", "radish", "cucumber"],
    "pepper": ["basil", "tomato", "parsley"],
    "potato": ["beans", "corn", "cabbage"]
}

def analyze_plant(plant_name: str, soil_moisture: float = 40.0, light_level: str = "medium", temperature: float = 22.0) -> dict:
    """
    Analyzes plant conditions and recommends care actions.
    Accepts plant_name and conditional data. Defaults are provided in case 
    the orchestrator only passes plant_name initially.
    """
    # Ensure inputs are the correct types to prevent crashes
    plant_name = str(plant_name).lower().strip() if plant_name else "unknown"
    light_level = str(light_level).lower().strip() if light_level else "medium"
    
    try:
        soil_moisture = float(soil_moisture)
    except (ValueError, TypeError):
        soil_moisture = 40.0
        
    try:
        temperature = float(temperature)
    except (ValueError, TypeError):
        temperature = 22.0
        
    recommendations = []
    
    # 2. Implement plant care logic.
    if soil_moisture < 30:
        recommendations.append("Water the plant today.")
        
    if light_level == "low":
        recommendations.append("Move plant to sunlight.")
        
    if temperature > 35:
        recommendations.append("Move plant to shade.")
        
    # 3. Implement a simple plant compatibility database.
    good_pairs = COMPATIBLE_PLANTS.get(plant_name, [])
    if good_pairs:
        recommendations.append(f"Consider companion planting with: {', '.join(good_pairs)}.")

    if not recommendations:
        recommendations.append("Plant conditions are optimal.")

    final_recommendation = " ".join(recommendations)
    
    # 4. Return response using shared format:
    return {
        "agent": "plant_agent",
        "status": "ok",
        "data": {
            "plant": plant_name,
            "moisture": str(soil_moisture),
            "light": light_level
        },
        "recommendation": final_recommendation
    }
