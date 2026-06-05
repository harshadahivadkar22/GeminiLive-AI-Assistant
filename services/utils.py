from datetime import datetime

def get_formatted_timestamp() -> str:
    """
    Returns the current system timestamp formatted consistently.
    
    Returns:
        str: Date-time string in 'YYYY-MM-DD HH:MM:SS' format.
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
