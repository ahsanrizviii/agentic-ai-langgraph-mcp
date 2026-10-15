# Task 03 — Weather MCP Server (AccuWeather)

An MCP server that returns current conditions plus a 12-hour forecast for any city, using the AccuWeather API.

Adapted from [adhikasp/mcp-weather](https://github.com/adhikasp/mcp-weather) (public domain — see [`LICENSE`](LICENSE)), with fixes needed to make it work against the current AccuWeather API.

## Fixes made to `weather.py`

1. **Authentication** — switched from the retired query-parameter auth (`?apikey=`) to the current Bearer scheme (`Authorization: Bearer <key>`).
2. **Cache bug** — the original code used `locations[0]` after a cache hit, raising `NameError` on the second query for the same city. The cache now stores the location key, name and country together.
3. **Transport security** — all requests use `https://`.

## Setup

```bash
cd mcp_tasks/task_03_weather_mcp_server
pip install -e .            # registers the mcp-weather command
cp .env.example .env        # then paste your AccuWeather key
```

Get a key from the [AccuWeather Developer Portal](https://developer.accuweather.com/). Requires Python 3.13+.

## Run

```bash
mcp-weather
```

## Claude Desktop

Use [`claude_config_snippet.json`](claude_config_snippet.json): point `command` at the `mcp-weather` executable on your machine and put your key in the `env` block.

## Test prompt

> Use the weather tool to get the hourly forecast for Rajshahi.

**Result:** real data returned — 29.8 °C, rain, plus a 12-hour forecast.

## Tool: `get_hourly_weather(location)`

Example response:

```json
{
  "location": "Jakarta",
  "location_key": "208971",
  "country": "Indonesia",
  "current_conditions": {
    "temperature": { "value": 32.2, "unit": "C" },
    "weather_text": "Partly sunny",
    "relative_humidity": 75,
    "precipitation": false,
    "observation_time": "2024-01-01T12:00:00+07:00"
  },
  "hourly_forecast": [
    {
      "relative_time": "+1 hour",
      "temperature": { "value": 32.2, "unit": "C" },
      "weather_text": "Partly sunny",
      "precipitation_probability": 40,
      "precipitation_type": "Rain",
      "precipitation_intensity": "Light"
    }
  ]
}
```
