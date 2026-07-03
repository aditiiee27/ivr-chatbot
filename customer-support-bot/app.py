import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
import config
from chatbot.database import (
    init_db, 
    save_customer, 
    save_chat_message, 
    get_chat_history, 
    save_feedback,
    get_customer_by_phone
)
from chatbot.llm_handler import generate_chatbot_response
from chatbot.speech import generate_speech, pregenerate_welcome_audio

app = Flask(__name__)
app.config.from_object(config)

# Initialize database tables and welcome assets on startup
with app.app_context():
    init_db()
    pregenerate_welcome_audio()

@app.route('/')
def index():
    """
    Renders the main IVR-style support dashboard.
    Generates a unique session_id if one doesn't exist.
    """
    session_id = request.args.get('session_id') or str(uuid.uuid4())
    return render_template('index.html', session_id=session_id)

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Processes a chat message sent by the user:
    1. Saves the user's message in the DB.
    2. Retrieves current session history.
    3. Generates Neer Sahayak's bilingual response via LLM (or fallback Mock).
    4. Converts the response text to speech in the appropriate language.
    5. Saves the response and its audio file name in the DB.
    6. Returns response text and audio file link as JSON.
    """
    data = request.json or {}
    session_id = data.get('session_id')
    message = data.get('message', '').strip()
    lang = data.get('lang', 'en') # 'en' or 'hi'
    
    if not session_id or not message:
        return jsonify({"error": "Missing session_id or message"}), 400

    try:
        # 1. Save user's message to DB
        save_chat_message(session_id, role="user", content=message)
        
        # 2. Get history to provide conversational memory
        history = get_chat_history(session_id)
        
        # 3. Generate response using Neer Sahayak's AI persona (passing in history for context)
        response_text = generate_chatbot_response(message, history)
        
        # Auto-detect language if not explicitly provided or default
        from chatbot.llm_handler import detect_language
        detected_lang = detect_language(response_text)
        
        # 4. Generate audio voice readout using gTTS in correct language
        audio_file = generate_speech(response_text, lang=detected_lang)
        
        # 5. Save assistant's response to DB
        save_chat_message(session_id, role="assistant", content=response_text, audio_file=audio_file)
        
        # 6. Return response to UI
        return jsonify({
            "response": response_text,
            "audio_file": f"/static/audio/{audio_file}" if audio_file else None
        })
    except Exception as e:
        app.logger.error(f"Error in /api/chat: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/customer', methods=['POST'])
def customer():
    """
    API endpoint to save customer registration details.
    """
    data = request.json or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    
    if not name or not email or not phone:
        return jsonify({"error": "All fields (name, email, phone) are required"}), 400
        
    customer_id = save_customer(name, email, phone)
    if customer_id:
        return jsonify({"status": "success", "customer_id": customer_id})
    else:
        # Check if we can pull the existing user to be helpful
        existing = get_customer_by_phone(phone)
        if existing:
            return jsonify({"status": "success", "customer_id": existing["id"], "message": "Existing customer loaded"})
        return jsonify({"error": "Failed to save customer details"}), 500

@app.route('/api/feedback', methods=['POST'])
def feedback():
    """
    API endpoint to record customer satisfaction ratings and comments.
    """
    data = request.json or {}
    session_id = data.get('session_id')
    rating = data.get('rating')
    comments = data.get('comments', '').strip()
    
    if not session_id or rating is None:
        return jsonify({"error": "Missing session_id or rating"}), 400
        
    feedback_id = save_feedback(session_id, int(rating), comments)
    if feedback_id:
        return jsonify({"status": "success", "feedback_id": feedback_id})
    else:
        return jsonify({"error": "Failed to save feedback"}), 500

@app.route('/api/history', methods=['GET'])
def history():
    """
    API endpoint to fetch session history logs.
    """
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400
        
    chat_logs = get_chat_history(session_id)
    return jsonify(chat_logs)

@app.route('/api/debug_db', methods=['GET'])
def debug_db():
    """
    Diagnostic API endpoint that pulls rows from sqlite database tables.
    Allows testing visibility of DB transactions directly from the browser.
    """
    try:
        from chatbot.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers ORDER BY created_at DESC LIMIT 10")
        customers = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM chat_history ORDER BY created_at DESC LIMIT 20")
        chats = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC LIMIT 10")
        feedback_list = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return jsonify({
            "customers": customers,
            "chats": chats,
            "feedback": feedback_list
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the server on port 5000 in debug mode for development
    app.run(host='0.0.0.0', port=5000, debug=True)
