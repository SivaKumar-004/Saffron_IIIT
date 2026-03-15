def analyze_plant(plant_name: str) -> dict:
    return {
        "agent": "plant_agent",
        "status": "ok",
        "data": {
            "plant": plant_name,
            "moisture": "",
            "light": ""
        },
        "recommendation": ""
    }
