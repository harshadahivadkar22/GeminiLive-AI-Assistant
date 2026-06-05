import re
import requests

def detect_bitcoin_query(query: str) -> bool:
    """
    Evaluates whether the user's prompt is requesting live Bitcoin or cryptocurrency
    price tracking information.
    
    Args:
        query (str): Input query prompt.
        
    Returns:
        bool: True if query matches a crypto price lookup pattern, False otherwise.
    """
    clean_query = query.strip().lower()
    
    # Exact keyword phrases indicating price lookup intent
    target_phrases = [
        "bitcoin price", "btc price", "crypto price",
        "price of bitcoin", "price of btc", "price of crypto",
        "bitcoin usd", "btc usd",
        "bitcoin rate", "btc rate",
        "bitcoin value", "btc value",
        "current price of btc", "current price of bitcoin"
    ]
    
    if any(phrase in clean_query for phrase in target_phrases):
        return True
        
    # Regex patterns for proximity-based keyword detection (e.g. "btc current rate", "price of space btc")
    patterns = [
        r'\b(?:bitcoin|btc|crypto)\b.*\b(?:price|rate|value|usd|cost)\b',
        r'\b(?:price|rate|value|cost)\b.*\b(?:bitcoin|btc|crypto)\b'
    ]
    
    for pattern in patterns:
        if re.search(pattern, clean_query):
            return True
            
    return False

def get_bitcoin_data() -> dict:
    """
    Sends a GET request to the CoinGecko simple price API to capture real-time
    USD valuation, total market cap, and 24h market change values for Bitcoin.
    
    Returns:
        dict: Parsed dictionary mapping USD price statistics.
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd',
        'include_market_cap': 'true',
        'include_24hr_change': 'true'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'bitcoin' in data:
                return data['bitcoin']
            raise ValueError("Response format from CoinGecko API was invalid.")
        elif response.status_code == 429:
            raise Exception("CoinGecko API Rate Limit exceeded (too many requests). Please wait a moment.")
        else:
            raise Exception(f"CoinGecko API returned status code {response.status_code}")
    except requests.Timeout:
        raise Exception("Connection timeout while contacting CoinGecko API.")
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch Bitcoin metrics due to a network error: {e}")

def format_bitcoin_response(data: dict) -> str:
    """
    Transforms CoinGecko raw values into a structured markdown response sheet.
    
    Args:
        data (dict): Bitcoin stats payload containing 'usd', 'usd_market_cap', and 'usd_24h_change'.
        
    Returns:
        str: Styled Markdown summary text.
    """
    price = data.get('usd', 0.0)
    market_cap = data.get('usd_market_cap', 0.0)
    change_24h = data.get('usd_24h_change', 0.0)
    
    # Large currency values formatting utility (T, B, M scaling)
    def format_market_cap(val):
        if val >= 1e12:
            return f"${val/1e12:,.2f} Trillion"
        elif val >= 1e9:
            return f"${val/1e9:,.2f} Billion"
        elif val >= 1e6:
            return f"${val/1e6:,.2f} Million"
        return f"${val:,.2f}"
        
    change_sign = "+" if change_24h >= 0 else ""
    change_emoji = "📈" if change_24h >= 0 else "📉"
    
    response = f"### 🪙 Bitcoin (BTC) Real-Time Metrics\n\n"
    response += f"* **Current Price:** ${price:,.2f} USD\n"
    response += f"* **Market Cap:** {format_market_cap(market_cap)} USD\n"
    response += f"* **24-Hour Change:** {change_emoji} `{change_sign}{change_24h:.2f}%`\n"
    return response
