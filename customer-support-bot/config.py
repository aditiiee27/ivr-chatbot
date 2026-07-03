import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Flask configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key-for-ivr-chatbot-internship")

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")

# Static directory for TTS audio output
AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio")

# Create audio directory if it doesn't exist yet
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# LLM API configuration
# Providers supported: "openai", "gemini", "mock" (offline fallback)
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "mock").lower()

# API Keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# LLM Model choices
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

# JSON Data configuration for Neer Nidaan Admin files
KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, "knowledge_base.json")
FAQ_DATA_PATH = os.path.join(BASE_DIR, "faq_data.json")
INTENTS_PATH = os.path.join(BASE_DIR, "intents.json")
DEPARTMENTS_PATH = os.path.join(BASE_DIR, "departments.json")
PORTAL_DATA_PATH = os.path.join(BASE_DIR, "portal_data.json")

