from config.settings import GEMINI_API_KEY
from google.genai import Client

def list_gemini_models():
    client = Client(api_key=GEMINI_API_KEY)
    
    
    models_pager = client.models.list()
    
    print("Available models:")
    for m in models_pager:
    
        print(f"- {m.name}")

if __name__ == "__main__":
    list_gemini_models()