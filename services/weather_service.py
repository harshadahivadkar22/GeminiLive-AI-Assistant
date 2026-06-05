import re
import requests
from config import Config

def extract_city(query: str) -> str:
    """
    Evaluates whether the user query is weather-related and parses it
    to extract the capitalized target city name.
    
    Query detection criteria:
    - Matches query strings such as "weather in Mumbai", "temperature for Paris today", "Delhi weather".
    
    Args:
        query (str): User input prompt.
        
    Returns:
        str: The isolated city name (properly capitalized), or None if no match is found.
    """
    clean_query = query.strip().lower()
    
    # List of regular expression patterns to isolate city names.
    # We match letters, spaces, hyphens, and apostrophes.
    patterns = [
        # Match phrases like "weather in Mumbai" or "temperature of Paris"
        r'\b(?:weather|temperature|temp|climate|forecast)\s+(?:in|of|for|at)\s+([a-zA-Z\s\-\']+)',
        # Match patterns like "weather Mumbai"
        r'\b(?:weather|temp|temperature)\s+([a-zA-Z\s\-\']+)',
        # Match patterns like "Mumbai weather"
        r'\b([a-zA-Z\s\-\']+)\s+(?:weather|temperature|temp|climate|forecast)\b'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, clean_query)
        if match:
            city = match.group(1).strip()
            
            # Remove trailing punctuation characters
            city = re.sub(r'[\?\.\!\,\;]', '', city).strip()
            
            # Remove common conversational filler words
            city = re.sub(r'\b(?:current|today|now|tomorrow|live|like|for|the)\b', '', city).strip()
            
            if city:
                return city.title()
                
    # Fallback keyword lookup: check if query contains core weather topics
    if any(k in clean_query for k in ['weather', 'temperature', 'temp', 'climate', 'forecast']):
        words = clean_query.split()
        candidate_words = [w for w in words if w not in [
            'weather', 'temperature', 'temp', 'climate', 'forecast',
            'current', 'today', 'now', 'tomorrow', 'live', 'what', 'is', 
            'the', 'like', 'in', 'of', 'for', 'at', 'me', 'tell', 'show', 'status'
        ]]
        if candidate_words:
            city = " ".join(candidate_words)
            city = re.sub(r'[\?\.\!\,\;]', '', city).strip()
            if city:
                return city.title()
                
    return None

def get_weather_data(city: str) -> dict:
    """
    Invokes the OpenWeatherMap Current Weather Data REST API for the target city.
    
    Args:
        city (str): Capitalized city name.
        
    Returns:
        dict: Raw JSON dictionary mapping temperature, wind speed, humidity, and condition.
    """
    if not Config.WEATHER_API_KEY:
        raise ValueError("WEATHER_API_KEY is not defined in config.")
        
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': Config.WEATHER_API_KEY,
        'units': 'metric'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise LookupError(f"City '{city}' was not found in the OpenWeatherMap records.")
        else:
            raise Exception(f"OpenWeatherMap API status {response.status_code}")
    except requests.RequestException as e:
        raise Exception(f"Failed to communicate with OpenWeatherMap: {e}")

def format_weather_response(city: str, data: dict) -> str:
    """
    Structures the weather JSON payload into a clean, markdown-styled text block.
    
    Args:
        city (str): The name of the city.
        data (dict): Raw weather metrics.
        
    Returns:
        str: Formatted Markdown string.
    """
    temp = data['main']['temp']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    condition = data['weather'][0]['description'].title()
    icon_code = data['weather'][0]['main'].lower()
    
    # Associate appropriate descriptive weather emojis
    emoji = "🌤"
    if "rain" in icon_code or "drizzle" in icon_code:
        emoji = "🌧"
    elif "cloud" in icon_code:
        emoji = "☁"
    elif "clear" in icon_code:
        emoji = "☀️"
    elif "snow" in icon_code:
        emoji = "❄"
    elif "thunderstorm" in icon_code:
        emoji = "⛈"
    elif any(term in icon_code for term in ["mist", "fog", "haze", "smoke"]):
        emoji = "🌫"
        
    response = f"### {emoji} Weather Report for **{city}**\n\n"
    response += f"* **Condition:** {condition}\n"
    response += f"* **Temperature:** {temp}°C\n"
    response += f"* **Humidity:** {humidity}%\n"
    response += f"* **Wind Speed:** {wind_speed} m/s\n"
    return response
