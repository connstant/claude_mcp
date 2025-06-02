from datetime import datetime
from datetime import timezone
from datetime import timedelta

def get_current_time():
    """
    Get the current date and time in Eastern Time.
    
    Returns:
        String with the current date and time in a readable format
    """
    # Get current time in UTC
    now_utc = datetime.now(timezone.utc)
    
    # Convert to Eastern Time (UTC-4 during daylight saving, UTC-5 otherwise)
    # This is a simplified approach - in production, use proper timezone libraries
    # For June 2025, we're in EDT (UTC-4)
    eastern_offset = timedelta(hours=-4)
    eastern_time = now_utc.replace(tzinfo=timezone.utc).astimezone(timezone(eastern_offset))
    
    # Format the time nicely
    return eastern_time.strftime("%Y-%m-%d %H:%M:%S %Z")
