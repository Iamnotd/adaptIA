"""
config.py
Configuración global y constantes de adaptIA.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ===== Identidad del asistente =====
ASSISTANT_NAME = "adaptIA"
WAKE_WORD = "orion"

# ===== Rutas SIN espacios para compatibilidad con Whisper =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = "C:\\adaptIA_temp"
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DB_PATH = os.path.join(BASE_DIR, "adaptia_memory.db")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# ===== API Keys =====
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", 587))

# ===== Modelo de IA (Groq - gratis) =====
GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 1024

# ===== Audio =====
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
SILENCE_THRESHOLD_SECONDS = 3.0
MAX_RECORDING_SECONDS = 30
MIN_TRANSCRIPTION_CONFIDENCE = 0.50

# ===== Whisper =====
WHISPER_MODEL_SIZE = "medium"
WHISPER_LANGUAGE = "es"

# ===== Memoria =====
MAX_CONTEXT_INTERACTIONS = 10

# ===== Palabras de confirmación / cancelación =====
CONFIRM_WORDS = ["si", "sí", "confirma", "confirmo", "adelante", "dale", "ok", "okay", "hazlo"]
CANCEL_WORDS = ["no", "cancela", "cancelar", "detente", "para", "stop"]
