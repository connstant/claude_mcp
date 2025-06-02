import datetime

def get_current_date() -> str:
    """Get the current date."""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d")