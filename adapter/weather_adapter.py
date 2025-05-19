import httpx

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict | None:
    """Make a request to the NWS API with proper error handling."""
    print(f"[weather_adapter] Fetching URL: {url}")
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            print(f"[weather_adapter] Response status: {response.status_code}")
            response.raise_for_status()
            json_data = response.json()
            print(f"[weather_adapter] Response JSON: {json_data}")
            return json_data
        except Exception as e:
            print(f"[weather_adapter] Exception during request: {e}")
            return None

async def fetch_alerts_from_api(state: str) -> dict:
    """Adapter: Fetch raw alerts data for a US state from the weather API."""
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    return await make_nws_request(url)

async def fetch_forecast_from_api(latitude: float, longitude: float) -> dict:
    """Adapter: Fetch raw forecast data for a location from the weather API."""
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    if not points_data:
        return None
    forecast_url = points_data["properties"]["forecast"]
    return await make_nws_request(forecast_url)
