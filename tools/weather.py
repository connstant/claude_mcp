from adapter import weather_adapter

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state."""
    try:
        data = await weather_adapter.fetch_alerts_from_api(state)
        if not data:
            return "Unable to fetch alerts. The weather service may be experiencing issues."
            
        if "features" not in data:
            return "Invalid alert data format. Missing 'features' field."
            
        if not data["features"]:
            return "No active alerts for this state."
            
        alerts = []
        for feature in data["features"]:
            try:
                alerts.append(format_alert(feature))
            except Exception as feature_err:
                print(f"Error formatting alert: {feature_err}")
                # Continue processing other alerts
                
        if not alerts:
            return "Error processing alerts data. No valid alerts could be processed."
            
        return "\n---\n".join(alerts)
    except Exception as e:
        return f"Error processing alerts data: {str(e)}"

async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location."""
    try:
        forecast_data = await weather_adapter.fetch_forecast_from_api(latitude, longitude)
        if not forecast_data:
            return "Unable to fetch detailed forecast. The weather service may be experiencing issues."
        
        # Check if the expected data structure exists
        if "properties" not in forecast_data:
            return f"Invalid forecast data format. Missing 'properties' field."
            
        if "periods" not in forecast_data["properties"]:
            return f"Invalid forecast data format. Missing 'periods' field."
            
        periods = forecast_data["properties"]["periods"]
        if not periods:
            return "No forecast periods available for this location."
            
        forecasts = []
        for period in periods[:5]:
            # Safely access dictionary values with .get() to avoid KeyError
            name = period.get('name', 'Unknown Period')
            temp = period.get('temperature', 'N/A')
            temp_unit = period.get('temperatureUnit', 'F')
            wind_speed = period.get('windSpeed', 'N/A')
            wind_dir = period.get('windDirection', 'N/A')
            forecast_text = period.get('detailedForecast', 'No detailed forecast available')
            
            forecast = f"""
{name}:
Temperature: {temp}°{temp_unit}
Wind: {wind_speed} {wind_dir}
Forecast: {forecast_text}
"""
            forecasts.append(forecast)
            
        return "\n---\n".join(forecasts)
    except Exception as e:
        return f"Error processing forecast data: {str(e)}"
