import httpx
import json

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

async def make_nws_request(url: str) -> dict | None:
    """Make a request to the NWS API with proper error handling."""
    print(f"[weather_adapter] Fetching URL: {url}")
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
        "Accept-Encoding": "gzip, deflate, br"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0, follow_redirects=True)
            print(f"[weather_adapter] Response status: {response.status_code}")
            response.raise_for_status()
            
            # Get the raw text first to debug any JSON parsing issues
            text_content = response.text
            if not text_content.strip():
                print("[weather_adapter] Error: Empty response received")
                return None
                
            try:
                json_data = response.json()
                return json_data
            except json.JSONDecodeError as json_err:
                print(f"[weather_adapter] JSON parsing error: {json_err}")
                print(f"[weather_adapter] Response content: {text_content[:200]}...")
                return None
                
        except httpx.HTTPStatusError as http_err:
            print(f"[weather_adapter] HTTP error: {http_err} (Status code: {http_err.response.status_code})")
            return None
        except httpx.RequestError as req_err:
            print(f"[weather_adapter] Request error: {req_err}")
            return None
        except Exception as e:
            print(f"[weather_adapter] Unexpected exception: {e}")
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
