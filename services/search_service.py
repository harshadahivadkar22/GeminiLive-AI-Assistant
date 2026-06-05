import re
import requests
from config import Config

def detect_search_query(query: str) -> bool:
    """
    Evaluates if a user's prompt requires real-time/grounded web data lookup.
    
    Keywords tracked:
    - latest news, current events, today's updates, recent developments.
    
    Args:
        query (str): Input query prompt.
        
    Returns:
        bool: True if query contains real-time news/event markers, False otherwise.
    """
    clean_query = query.strip().lower()
    
    # Specific targeted news/update terms
    target_phrases = [
        "latest news", "current events", "today's updates", "recent developments",
        "today's news", "live updates", "recent news", "latest updates"
    ]
    
    if any(phrase in clean_query for phrase in target_phrases):
        return True
        
    # Proximity regex patterns matching live indicator keywords
    patterns = [
        r'\b(?:latest|current|today|recent|live)\b.*\b(?:news|events|updates|developments|status)\b',
        r'\b(?:news|events|updates|developments|status)\b.*\b(?:latest|current|today|recent|live)\b'
    ]
    
    for pattern in patterns:
        if re.search(pattern, clean_query):
            return True
            
    return False

def google_search(query: str) -> list:
    """
    Sends a query to Google Custom Search JSON API to retrieve top 3 search results.
    
    Args:
        query (str): Grounding search terms.
        
    Returns:
        list: Structured list of dictionaries containing 'title', 'link', and 'snippet'.
    """
    if not Config.GOOGLE_SEARCH_API_KEY or not Config.SEARCH_ENGINE_ID:
        print("Warning: Google Custom Search credentials are not set. Web search will be skipped.")
        return []
        
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': Config.GOOGLE_SEARCH_API_KEY,
        'cx': Config.SEARCH_ENGINE_ID,
        'q': query,
        'num': 3
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            results = []
            for item in items:
                # Fallback to link URL or default text if title/snippet are empty
                title = item.get('title', '').strip() or "Untitled Web Result"
                link = item.get('link', '').strip()
                snippet = item.get('snippet', '').strip() or "No summary snippet available for this site."
                
                if link:
                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet
                    })
            return results
        else:
            print(f"Google Custom Search API status {response.status_code}: {response.text}")
            return []
    except requests.Timeout:
        print("Timeout connecting to Google Custom Search API.")
        return []
    except requests.RequestException as e:
        print(f"Google Custom Search API connection error: {e}")
        return []

def format_search_context(results: list) -> str:
    """
    Structures the search results array into a formatted context block
    for model prompt instructions.
    
    Args:
        results (list): Results dictionaries list.
        
    Returns:
        str: Grounding context text block.
    """
    if not results:
        return "No relevant web search results were found for this query."
        
    context_blocks = []
    for idx, result in enumerate(results, start=1):
        block = (
            f"Result {idx}:\n"
            f"Title: {result['title']}\n"
            f"URL: {result['link']}\n"
            f"Summary Snippet: {result['snippet']}\n"
        )
        context_blocks.append(block)
        
    return "\n---\n".join(context_blocks)
