from datetime import datetime, date

def parse_iso_date(date_str: str) -> date:
    """
    Parses a YYYY-MM-DD date string into a datetime.date object.
    
    Args:
        date_str (str): The date string in YYYY-MM-DD format.
        
    Returns:
        date: A date object if parsing succeeds, otherwise None.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

def categorize_deadline(deadline_date_str: str, today: date = None) -> str:
    """
    Categorizes a deadline date string into Urgent, Upcoming, Future, or Overdue.
    
    Categories:
    - Urgent: Within 1 day (today or tomorrow)
    - Upcoming: Within 7 days
    - Future: More than 7 days
    - Overdue: Prior to today
    
    Args:
        deadline_date_str (str): The deadline date in YYYY-MM-DD format.
        today (date, optional): Reference date. Defaults to today's date.
        
    Returns:
        str: Category name ('URGENT', 'UPCOMING', 'FUTURE', 'OVERDUE', or 'UNKNOWN').
    """
    if not today:
        today = date.today()
        
    deadline_date = parse_iso_date(deadline_date_str)
    if not deadline_date:
        return "UNKNOWN"
        
    delta_days = (deadline_date - today).days
    
    if delta_days < 0:
        return "OVERDUE"
    elif delta_days <= 1:
        return "URGENT"
    elif delta_days <= 7:
        return "UPCOMING"
    else:
        return "FUTURE"

def get_days_remaining(deadline_date_str: str, today: date = None) -> int:
    """
    Calculates the number of days remaining until the deadline.
    
    Args:
        deadline_date_str (str): The deadline date in YYYY-MM-DD format.
        today (date, optional): Reference date. Defaults to today's date.
        
    Returns:
        int: Number of days remaining (negative if overdue), or None if invalid date.
    """
    if not today:
        today = date.today()
        
    deadline_date = parse_iso_date(deadline_date_str)
    if not deadline_date:
        return None
        
    return (deadline_date - today).days

def format_date_friendly(date_str: str, today: date = None) -> str:
    """
    Formats an ISO date string into a friendly human-readable format.
    E.g. "Tomorrow", "Today", "Yesterday", or "July 05, 2026"
    
    Args:
        date_str (str): The ISO date string (YYYY-MM-DD).
        today (date, optional): Reference date. Defaults to today's date.
        
    Returns:
        str: Friendly date string.
    """
    if not today:
        today = date.today()
        
    target_date = parse_iso_date(date_str)
    if not target_date:
        return date_str  # Return original if parsing fails
        
    delta_days = (target_date - today).days
    
    if delta_days == 0:
        return "Today"
    elif delta_days == 1:
        return "Tomorrow"
    elif delta_days == -1:
        return "Yesterday"
    else:
        # Standard format like "July 5, 2026"
        return target_date.strftime("%B %d, %Y")
