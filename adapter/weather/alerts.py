"""
Weather alerts functionality.
"""

from adapter.weather.client import make_nws_request, NWS_API_BASE

async def fetch_alerts_from_api(state: str) -> dict:
    """
    Adapter: Fetch raw alerts data for a US state from the weather API.
    
    Args:
        state: Two-letter US state code (e.g., 'CA', 'NY')
        
    Returns:
        Dictionary with weather alerts data or None if request failed
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    return await make_nws_request(url)
