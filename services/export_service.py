import os
from datetime import datetime
from services.utils import get_formatted_timestamp

def export_chat_txt(history: list) -> str:
    """
    Formats the conversation history list into a clean text document representation.
    
    Args:
        history (list): List of chat pairs with 'user', 'assistant', and optional 'timestamp'.
        
    Returns:
        str: Formatted text file content.
    """
    export_time = get_formatted_timestamp()
    content = []
    
    content.append("==================================================")
    content.append("   GEMINILIVE AI ASSISTANT - CHAT EXPORT")
    content.append(f"   Export Time: {export_time}")
    content.append("==================================================\n")
    
    if not history:
        content.append("No conversation history found.")
        return "\n".join(content)
        
    for idx, pair in enumerate(history, start=1):
        ts = pair.get('timestamp', 'Unknown Time')
        user_msg = pair.get('user', '').strip()
        assistant_msg = pair.get('assistant', '').strip()
        
        content.append(f"Turn #{idx} - [{ts}]")
        content.append(f"USER: {user_msg}")
        content.append(f"ASSISTANT:\n{assistant_msg}")
        content.append("\n" + "-" * 50 + "\n")
        
    return "\n".join(content)

def export_chat(history: list) -> tuple:
    """
    Generates the text export, names it with a timestamp, writes it to
    the exports/ folder, and returns the filepath and filename.
    
    Args:
        history (list): Chat logs to format.
        
    Returns:
        tuple: (filepath, filename)
    """
    export_dir = 'exports'
    os.makedirs(export_dir, exist_ok=True)
    
    # Generate timestamped filename using clean file-compatible format
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"chat_export_{timestamp}.txt"
    filepath = os.path.join(export_dir, filename)
    
    # Generate the text content
    file_content = export_chat_txt(history)
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(file_content)
        
    return filepath, filename
