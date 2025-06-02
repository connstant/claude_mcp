from adapter.weather import fetch_alerts_from_api

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
        data = await fetch_alerts_from_api(state)
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
