import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
PORT = int(os.getenv("PORT", 8000))
TABPFN_TOKEN = os.getenv("TABPFN_TOKEN", "")
