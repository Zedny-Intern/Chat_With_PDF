from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")  

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("Loaded GEMINI_API_KEY:", GEMINI_API_KEY)
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
