import datetime

def today():
    """Return current date in ISO format."""
    return datetime.datetime.now().date().isoformat()
