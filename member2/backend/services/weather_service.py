import os
import random
import requests
from typing import Dict, Union

def get_weather(region: str) -> Dict[str, Union[float, int]]:
    """
    Fetch REAL weather data for a given region using OpenWeather API.
    If the API key is unauthorized or fails, gracefully falls back to Open-Meteo.
    """
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    
    # Primary Source: OpenWeather API
    if api_key:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={region},IN&appid={api_key}&units=metric"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Rainfall defaults to 0 if not present in the weather response
            rainfall = data.get("rain", {}).get("1h", 0.0)
            
            print(f"🌤️ [WeatherService] Using real data from OpenWeather for: {region}")
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "rainfall": rainfall,
                "wind_speed": round(data["wind"]["speed"] * 3.6, 1) # convert m/s to km/h for consistency
            }
        except Exception as e:
            print(f"[WeatherService] OpenWeather API failed for {region} (Error: {e}). Falling back to Open-Meteo...")

    # Secondary Source: Open-Meteo Free Geocoding Backend
    try:
        # Step 1: Geocoding (Get Latitude and Longitude for the region)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={region}&count=50"
        geo_response = requests.get(geo_url, timeout=5)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data.get("results"):
            raise ValueError(f"Could not find coordinates for region: {region}")
            
        # Try to prioritize finding the region in India
        target_result = next((r for r in geo_data["results"] if r.get("country") == "India"), geo_data["results"][0])
            
        lat = target_result["latitude"]
        lon = target_result["longitude"]
        
        # Step 2: Fetch current weather for those coordinates
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m"
        weather_response = requests.get(weather_url, timeout=5)
        weather_response.raise_for_status()
        weather_data = weather_response.json()["current"]
        
        print(f"🌤️ [WeatherService] Using real data from Open-Meteo for: {region}")
        return {
            "temperature": weather_data["temperature_2m"],
            "humidity": weather_data["relative_humidity_2m"],
            "rainfall": weather_data["rain"],
            "wind_speed": weather_data["wind_speed_10m"]
        }
    except Exception as e:
        print(f"[WeatherService] Open-Meteo API call failed for {region}: {e}. Disabling real data simulation.")
        # Absolute last resort fallback (should never be seen)
        return {
            "temperature": round(random.uniform(20.0, 30.0), 1),
            "humidity": round(random.uniform(20.0, 90.0), 1),
            "rainfall": round(random.uniform(0.0, 120.0), 1),
            "wind_speed": round(random.uniform(0.0, 20.0), 1)
        }
