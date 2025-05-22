import datetime

def get_current_time() -> str:
    """Get the current date and time."""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_current_date() -> str:
    """Get the current date."""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d")

def get_timezone() -> str:
    """Get the current timezone."""
    now = datetime.datetime.now().astimezone()
    return str(now.tzinfo)
