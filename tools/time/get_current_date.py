from datetime import datetime, timezone, timedelta

def get_current_date() -> str:
    """Get the current date."""
    # Get current time in UTC
    now_utc = datetime.now(timezone.utc)
    
    # Convert to Eastern Time (UTC-4 during daylight saving, UTC-5 otherwise)
    # For June 2025, we're in EDT (UTC-4)
    eastern_offset = timedelta(hours=-4)
    eastern_time = now_utc.replace(tzinfo=timezone.utc).astimezone(timezone(eastern_offset))
    return eastern_time.strftime("%Y-%m-%d")