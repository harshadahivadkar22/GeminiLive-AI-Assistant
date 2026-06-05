import os
import json

MEMORY_FILE = os.path.join('memory', 'chat_history.json')

def load_chat_history() -> list:
    """
    Loads previous chat history from memory/chat_history.json.
    
    Returns:
        list: A list of dictionaries representing the chat history, 
              e.g., [{"user": "...", "assistant": "..."}, ...]
    """
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading chat history: {e}")
        # In case of corruption, return an empty history
        return []

def save_chat_history(history: list) -> None:
    """
    Saves the provided chat history to memory/chat_history.json.
    
    Args:
        history (list): The list of dictionaries representing chat history.
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving chat history: {e}")

def clear_chat_history() -> None:
    """
    Clears all chat history by overwriting the JSON file with an empty list.
    """
    save_chat_history([])
