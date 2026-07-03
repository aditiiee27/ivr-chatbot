import os
import hashlib
from gtts import gTTS
import config

def generate_speech(text, lang='en'):
    """
    Converts text to speech (TTS) using gTTS and returns the filename.
    Implements a caching mechanism:
    1. Computes an MD5 hash of the response text and language.
    2. If an MP3 for this hash already exists in static/audio/, returns the existing file.
    3. Otherwise, generates a new MP3 using gTTS and saves it.
    4. Handles exceptions gracefully (e.g., if internet is offline).
    
    Returns:
        str: The name of the generated audio file (e.g., 'a8f9e2...mp3')
             or None if TTS fails.
    """
    if not text:
        return None

    # Clean text to make hashing consistent
    clean_text = text.strip()
    
    # Generate MD5 hash of the text + language to serve as a unique filename
    hash_object = hashlib.md5(f"{clean_text}_{lang}".encode('utf-8'))
    file_id = hash_object.hexdigest()
    filename = f"{file_id}.mp3"
    filepath = os.path.join(config.AUDIO_DIR, filename)

    # 1. Caching: If the file already exists, reuse it!
    if os.path.exists(filepath):
        print(f"TTS Cache Hit: {filename} ({lang})")
        return filename

    # 2. Cache Miss: Generate the speech audio file
    try:
        print(f"TTS Cache Miss: Generating voice file in '{lang}' for '{clean_text[:30]}...'")
        
        # gTTS translates text into speech. lang='en' for English, lang='hi' for Hindi
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        tts.save(filepath)
        
        return filename
    except Exception as e:
        print(f"Error generating text-to-speech audio: {e}")
        return None

def pregenerate_welcome_audio():
    """
    Pregenerates both English and Hindi welcome audio files on server startup.
    """
    welcomes = {
        "welcome_en.mp3": ("Hello! Welcome to the Neer Nidaan Grievance Assistant portal. How can I help you today?", "en"),
        "welcome_hi.mp3": ("नमस्कार! नीर निदान शिकायत सहायक पोर्टल पर आपका स्वागत है। आज मैं आपकी क्या सहायता कर सकता हूँ?", "hi")
    }
    
    for filename, (text, lang) in welcomes.items():
        filepath = os.path.join(config.AUDIO_DIR, filename)
        if not os.path.exists(filepath):
            try:
                print(f"Pregenerating welcome audio: {filename} ({lang})...")
                tts = gTTS(text=text, lang=lang, slow=False)
                tts.save(filepath)
                print(f"Welcome audio {filename} pregenerated successfully.")
            except Exception as e:
                print(f"Failed to pregenerate welcome audio {filename}: {e}")

