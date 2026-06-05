from flask import Flask, request, jsonify, render_template, send_file
from services.gemini_service import generate_gemini_response, generate_gemini_response_with_search
from services.memory_service import load_chat_history, save_chat_history, clear_chat_history
from services.weather_service import extract_city, get_weather_data, format_weather_response
from services.bitcoin_service import detect_bitcoin_query, get_bitcoin_data, format_bitcoin_response
from services.search_service import detect_search_query, google_search, format_search_context
from services.export_service import export_chat
from services.utils import get_formatted_timestamp

app = Flask(__name__)

@app.route('/')
def index():
    """
    Renders the chat interface home page.
    """
    return render_template('index.html')

@app.route('/api/history', methods=['GET'])
def get_history():
    """
    Retrieves the stored chat history from the JSON file.
    """
    history = load_chat_history()
    return jsonify(history)

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """
    Clears all stored conversation history.
    """
    clear_chat_history()
    return jsonify({'status': 'success', 'message': 'Chat history cleared successfully.'})

@app.route('/api/export', methods=['GET'])
def download_export():
    """
    Generates a timestamped TXT export file of the chat history
    and sends it to the browser as an attachment.
    """
    try:
        history = load_chat_history()
        filepath, filename = export_chat(history)
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        print(f"Error in export route: {e}")
        return jsonify({'error': f"Failed to export chat history: {str(e)}"}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handles user chat messages. Checks intents in the following order:
    1. Bitcoin/crypto price lookup -> CoinGecko API
    2. Real-time search query -> Google Custom Search -> Gemini answering with context
    3. Weather query -> OpenWeatherMap API
    4. General query -> standard Gemini
    Saves the user prompt and final formatted response in the 20-pair conversation memory.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request: No data provided'}), 400
        
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
        
    try:
        # 1. Load existing history context from JSON
        history = load_chat_history()
        history = history[-20:]
        
        # 2. Check for Bitcoin/crypto price lookup intent
        if detect_bitcoin_query(user_message):
            try:
                btc_info = get_bitcoin_data()
                bot_response = format_bitcoin_response(btc_info)
            except Exception as e:
                bot_response = f"Sorry, I encountered an error fetching Bitcoin metrics: {str(e)}"
                
        # 3. Check for real-time information search intent
        elif detect_search_query(user_message):
            try:
                # Fetch top search results
                search_results = google_search(user_message)
                if search_results:
                    search_context = format_search_context(search_results)
                    # Ask Gemini to answer using search context
                    bot_response = generate_gemini_response_with_search(user_message, history, search_context)
                else:
                    # Fallback to general Gemini if no search results returned
                    bot_response = generate_gemini_response(user_message, history)
            except Exception as e:
                bot_response = f"Sorry, I encountered an error performing web search: {str(e)}"
                
        # 4. Check for weather query intent
        else:
            detected_city = extract_city(user_message)
            if detected_city:
                try:
                    weather_info = get_weather_data(detected_city)
                    bot_response = format_weather_response(detected_city, weather_info)
                except LookupError:
                    bot_response = f"Could not find weather data for **{detected_city}**. Please check the spelling and try again."
                except Exception as e:
                    bot_response = f"Sorry, I encountered an error fetching the weather: {str(e)}"
            else:
                # General query: Call Gemini service with prompt and history context
                bot_response = generate_gemini_response(user_message, history)
        
        # 5. Append the new message pair to history and save (with timestamp)
        history.append({
            'user': user_message,
            'assistant': bot_response,
            'timestamp': get_formatted_timestamp()
        })
        
        history = history[-20:]
        save_chat_history(history)
        
        return jsonify({'response': bot_response})
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error in chat route: {error_msg}")
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    # Run the application locally on port 5000
    app.run(debug=True, port=5000)
