import re
import random
import json
import os
import config

# Initialize LLM Clients conditionally
openai_client = None
if config.OPENAI_API_KEY:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")

gemini_available = False
if config.GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=config.GEMINI_API_KEY)
        gemini_available = True
    except Exception as e:
        print(f"Failed to initialize Gemini API client: {e}")


def load_json_file(filepath, default):
    """Loads a JSON file dynamically to ensure admin changes are live."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return default


def get_latest_system_prompt():
    """Generates the system prompt dynamically using the latest JSON files."""
    kb = load_json_file(config.KNOWLEDGE_BASE_PATH, {})
    faqs = load_json_file(config.FAQ_DATA_PATH, [])
    depts = load_json_file(config.DEPARTMENTS_PATH, [])
    portal = load_json_file(config.PORTAL_DATA_PATH, {})

    # Format Departments
    dept_str = ""
    for d in depts:
        dept_str += f"- {d.get('code')}: {d.get('name_en')} ({d.get('name_hi')}) - {d.get('description_en')} / {d.get('description_hi')}\n"

    # Format Grievance Channels
    channel_str = ""
    for ch in portal.get("complaint_channels", []):
        channel_str += f"- {ch.get('channel')}:\n"
        for step in ch.get("steps_en", []):
            channel_str += f"  * {step}\n"

    # Format FAQs
    faq_str = ""
    for item in faqs:
        faq_str += f"- Question: {item.get('question_en')} / {item.get('question_hi')}\n"
        faq_str += f"  Answer: {item.get('answer_en')} / {item.get('answer_hi')}\n"

    prompt = f"""
You are "Neer Sahayak" (Water Grievance Redressal Assistant), a helpful, friendly, and bilingual (Hindi/English) AI support assistant for the UP Government's "Neer Nidaan" water grievance portal.

Your tone must be:
1. Polite, respectful, professional, and citizen-friendly.
2. Concise: Keep your responses relatively short (1-3 sentences) so that it sounds natural when read aloud.
3. Dual-Language Adaptive: Answer in Hindi if the citizen writes in Hindi, and in English if they write in English.

Portal Context:
- Portal Name: Neer Nidaan (नीर निदान)
- Organization: {kb.get('organization_en')} ({kb.get('organization_hi')})
- Helpline Toll-Free: {kb.get('helpline')}
- Mission: {kb.get('mission_en')} ({kb.get('mission_hi')})
- Services: {', '.join(portal.get('services_en', []))} / {', '.join(portal.get('services_hi', []))}

Official Departments:
{dept_str}

Grievance Channels & Steps:
{channel_str}

Bilingual FAQs for reference:
{faq_str}

Rules:
1. GREETING: Welcome citizens warmly. Help them register complaints or track complaints.
2. COMPLAINT LODGING: Collect citizen name, phone number, location, and issue type step-by-step.
3. FRUSTRATION: Apologize and offer immediate supervisor callback details collection.
4. CONSTRAINTS: Speak as an official assistant. Do not mention you are an AI or language model.
"""
    return prompt.strip()


def detect_language(text):
    """Basic check to see if the user query contains Hindi characters or keywords."""
    # Check for Hindi unicode range
    if re.search(r'[\u0900-\u097F]', text):
        return 'hi'
    # Check for common Hindi keywords typed in English (Hinglish)
    hinglish_keywords = ['paani', 'pani', 'shikayat', 'jila', 'gaon', 'namaste', ' helpline', 'samashya', 'samanya', 'road', 'sadak', 'pipe']
    text_lower = text.lower()
    if any(k in text_lower for k in hinglish_keywords):
        return 'hi'
    return 'en'


def get_mock_response(user_message, history):
    """
    Offline bilingual dialogue engine mapping keywords/intents from JSON to answers.
    Tracks state dynamically by inspecting the conversation history.
    """
    msg = user_message.lower().strip()
    lang = detect_language(user_message)

    # Dynamic JSON data loading
    kb = load_json_file(config.KNOWLEDGE_BASE_PATH, {})
    faqs = load_json_file(config.FAQ_DATA_PATH, [])
    intents = load_json_file(config.INTENTS_PATH, {})
    portal = load_json_file(config.PORTAL_DATA_PATH, {})

    # Extract last assistant message for context tracking
    last_assistant_msg = ""
    for h in reversed(history):
        if h['role'] == 'assistant':
            last_assistant_msg = h['content'].lower()
            break

    # --- DIALOGUE STATE: Callback Registration Flow ---
    if "शुभ नाम" in last_assistant_msg or "your name" in last_assistant_msg:
        name = user_message.strip()
        if lang == 'hi':
            return f"धन्यवाद, {name}। कृपया अपना 10 अंकों का मोबाइल नंबर साझा करें ताकि हमारे अधिकारी आपसे संपर्क कर सकें।"
        else:
            return f"Thank you, {name}. Please share your 10-digit mobile number so our officers can contact you."

    if "मोबाइल नंबर" in last_assistant_msg or "mobile number" in last_assistant_msg or "phone number" in last_assistant_msg:
        phone_match = re.search(r'\b\d{10}\b', user_message)
        phone = phone_match.group(0) if phone_match else user_message.strip()
        if lang == 'hi':
            return f"पंजीकृत कर लिया गया है। आपका संपर्क नंबर {phone} है। वरिष्ठ अधिकारी जल्द ही आपसे संपर्क करेंगे। क्या मैं अन्य सहायता कर सकता हूँ?"
        else:
            return f"Registered successfully. Your callback contact is {phone}. A senior officer will reach out to you shortly. Can I help you with anything else?"

    # --- DIALOGUE STATE: Registering Grievance Flow (Bilingual) ---
    if "शिकायत दर्ज" in msg or "register complaint" in msg or "lodge complaint" in msg:
        if lang == 'hi':
            return "नया जल शिकायत दर्ज करने में खुशी होगी। कृपया अपना नाम बताएं।"
        else:
            return "I'd be glad to help you register a water grievance. Please tell me your full name."

    # --- INTENT 1: Greetings ---
    greet_keywords = intents.get("greetings", {}).get("keywords", [])
    if any(k in msg for k in greet_keywords):
        return intents["greetings"]["response_hi"] if lang == 'hi' else intents["greetings"]["response_en"]

    # --- INTENT 2: Frustration Escalation ---
    frust_keywords = intents.get("frustration", {}).get("keywords", [])
    if any(k in msg for k in frust_keywords):
        return intents["frustration"]["response_hi"] if lang == 'hi' else intents["frustration"]["response_en"]

    # --- INTENT 3: Help Options ---
    help_keywords = intents.get("help", {}).get("keywords", [])
    if any(k in msg for k in help_keywords):
        return intents["help"]["response_hi"] if lang == 'hi' else intents["help"]["response_en"]

    # --- INTENT 4: Complaint Tracking ---
    if "track" in msg or "status" in msg or "ट्रैक" in msg or "स्थिति" in msg or "चेक" in msg:
        # Check if user provided a complaint number
        complaint_match = re.search(r'\b(nn-\d{4}-\d{5}|\d{5,6})\b', msg)
        if complaint_match:
            c_num = complaint_match.group(0).upper()
            if lang == 'hi':
                return f"शिकायत संख्या {c_num} वर्तमान में प्रगति पर है। जल निगम (ग्रामीण) के क्षेत्रीय अभियंता को आवंटित कर दी गई है। समय पर समाधान किया जाएगा।"
            else:
                return f"Grievance number {c_num} is currently in progress. It has been assigned to the regional engineer of UP Jal Nigam (Rural). It will be resolved shortly."
        else:
            if lang == 'hi':
                return "शिकायत ट्रैक करने के लिए कृपया अपनी शिकायत संख्या (उदा. NN-2026-12345) साझा करें, या पोर्टल में लॉगिन करें।"
            else:
                return "To track your grievance, please share your complaint number (e.g., NN-2026-12345), or log in to the portal dashboard."

    # --- INTENT 5: FAQ Keyword Matching ---
    best_faq = None
    max_matches = 0
    for faq in faqs:
        matches = 0
        for kw in faq.get("keywords", []):
            if kw in msg:
                matches += 1
        if matches > max_matches:
            max_matches = matches
            best_faq = faq

    if best_faq and max_matches > 0:
        return best_faq["answer_hi"] if lang == 'hi' else best_faq["answer_en"]

    # --- FALLBACK ---
    if lang == 'hi':
        return f"माफ़ कीजिये, मुझे इसके बारे में पूरी जानकारी नहीं मिली। आप टोल-फ्री हेल्पलाइन {kb.get('helpline', '18001212165')} पर संपर्क कर सकते हैं या अपना प्रश्न अलग तरीके से पूछ सकते हैं।"
    else:
        return f"I'm sorry, I couldn't find exact information for that. You can contact our toll-free helpline at {kb.get('helpline', '18001212165')} or rephrase your question."


def generate_chatbot_response(user_message, history):
    """
    Orchestrates the response generation.
    Checks the configured provider:
    - If provider is 'openai' and key is present, calls OpenAI chat completions.
    - If provider is 'gemini' and key is present, calls Gemini API.
    - Otherwise (or on failure), falls back to the local rule-based mock engine.
    """
    provider = config.LLM_PROVIDER
    
    # Validation: Fallback automatically if credentials are not set
    if provider == "openai" and not config.OPENAI_API_KEY:
        provider = "mock"
    elif provider == "gemini" and not config.GEMINI_API_KEY:
        provider = "mock"

    latest_prompt = get_latest_system_prompt()

    if provider == "openai":
        try:
            messages = [{"role": "system", "content": latest_prompt}]
            # Add latest 10 messages from history to keep prompt size under control
            for chat in history[-10:]:
                messages.append({"role": chat["role"], "content": chat["content"]})
            messages.append({"role": "user", "content": user_message})

            response = openai_client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                max_tokens=250,
                temperature=0.6
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}. Falling back to offline mock engine.")
            return get_mock_response(user_message, history)

    elif provider == "gemini":
        try:
            model = genai.GenerativeModel(
                model_name=config.GEMINI_MODEL,
                system_instruction=latest_prompt
            )
            
            # Format history for Gemini SDK
            contents = []
            for chat in history[-10:]:
                role = "user" if chat["role"] == "user" else "model"
                contents.append({"role": role, "parts": [chat["content"]]})
            contents.append({"role": "user", "parts": [user_message]})

            response = model.generate_content(contents)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API error: {e}. Falling back to offline mock engine.")
            return get_mock_response(user_message, history)

    else: # mock provider
        return get_mock_response(user_message, history)
