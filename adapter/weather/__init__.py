"""
Weather adapter package for weather data integration.
"""

# Export all weather-related functions
from adapter.weather.client import make_nws_request
from adapter.weather.alerts import fetch_alerts_from_api
from adapter.weather.forecast import fetch_forecast_from_api
