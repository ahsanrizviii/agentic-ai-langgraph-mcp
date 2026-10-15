import os
import json
from pathlib import Path
from typing import Dict, Optional
from fastmcp import FastMCP
from dotenv import load_dotenv
from aiohttp import ClientSession

load_dotenv()

mcp = FastMCP("mcp-weather")

CACHE_DIR = Path.home() / ".cache" / "weather"
LOCATION_CACHE_FILE = CACHE_DIR / "location_cache.json"


def get_cached_location(location: str) -> Optional[dict]:
    if not LOCATION_CACHE_FILE.exists():
        return None
    try:
        with open(LOCATION_CACHE_FILE, "r") as f:
            cache = json.load(f)
            return cache.get(location)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def cache_location(location: str, info: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        if LOCATION_CACHE_FILE.exists():
            with open(LOCATION_CACHE_FILE, "r") as f:
                cache = json.load(f)
        else:
            cache = {}
        cache[location] = info
        with open(LOCATION_CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to cache location: {e}")


@mcp.tool()
async def get_hourly_weather(location: str) -> Dict:
    """Get hourly weather forecast for a location."""
    api_key = os.getenv("ACCUWEATHER_API_KEY")
    base_url = "https://dataservice.accuweather.com"
    headers = {"Authorization": f"Bearer {api_key}"}

    cached = get_cached_location(location)
    if cached:
        location_key = cached["key"]
        location_name = cached["name"]
        location_country = cached["country"]
    else:
        async with ClientSession() as session:
            url = f"{base_url}/locations/v1/cities/search"
            async with session.get(url, headers=headers, params={"q": location}) as response:
                locations = await response.json()
                if response.status != 200:
                    raise Exception(f"Error fetching location data: {response.status}, {locations}")
                if not locations:
                    raise Exception("Location not found")
            location_key = locations[0]["Key"]
            location_name = locations[0]["LocalizedName"]
            location_country = locations[0]["Country"]["LocalizedName"]
            cache_location(location, {
                "key": location_key,
                "name": location_name,
                "country": location_country,
            })

    async with ClientSession() as session:
        url = f"{base_url}/currentconditions/v1/{location_key}"
        async with session.get(url, headers=headers) as response:
            current_conditions = await response.json()

        url = f"{base_url}/forecasts/v1/hourly/12hour/{location_key}"
        async with session.get(url, headers=headers, params={"metric": "true"}) as response:
            forecast = await response.json()

    hourly_data = []
    for i, hour in enumerate(forecast, 1):
        hourly_data.append({
            "relative_time": f"+{i} hour{'s' if i > 1 else ''}",
            "temperature": {
                "value": hour["Temperature"]["Value"],
                "unit": hour["Temperature"]["Unit"],
            },
            "weather_text": hour["IconPhrase"],
            "precipitation_probability": hour["PrecipitationProbability"],
            "precipitation_type": hour.get("PrecipitationType"),
            "precipitation_intensity": hour.get("PrecipitationIntensity"),
        })

    if current_conditions and len(current_conditions) > 0:
        current = current_conditions[0]
        current_data = {
            "temperature": {
                "value": current["Temperature"]["Metric"]["Value"],
                "unit": current["Temperature"]["Metric"]["Unit"],
            },
            "weather_text": current["WeatherText"],
            "relative_humidity": current.get("RelativeHumidity"),
            "precipitation": current.get("HasPrecipitation", False),
            "observation_time": current["LocalObservationDateTime"],
        }
    else:
        current_data = "No current conditions available"

    return {
        "location": location_name,
        "location_key": location_key,
        "country": location_country,
        "current_conditions": current_data,
        "hourly_forecast": hourly_data,
    }