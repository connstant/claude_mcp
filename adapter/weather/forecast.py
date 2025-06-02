"""
Weather forecast functionality.
"""

from adapter.weather.client import make_nws_request, NWS_API_BASE

async def fetch_forecast_from_api(latitude: float, longitude: float) -> dict:
    """
    Adapter: Fetch raw forecast data for a location from the weather API.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Dictionary with weather forecast data or None if request failed
    """
    # First, get the forecast URL for this location
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    
    if not points_data or "properties" not in points_data:
        return None
    
    # Extract the forecast URL from the points response
    forecast_url = points_data["properties"].get("forecast")
    if not forecast_url:
        return None
    
    # Now fetch the actual forecast
    return await make_nws_request(forecast_url)
