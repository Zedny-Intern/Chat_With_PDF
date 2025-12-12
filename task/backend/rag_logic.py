import google.generativeai as genai
from config.settings import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(context_list: list, chat_history: list, question: str):
    context_str = "\n\n".join(context_list)

    history_text = ""
    for msg in chat_history[-5:]:
        history_text += f"{msg['role'].upper()}: {msg['content']}\n"

    # Build prompt
    prompt = f"""
You are a helpful AI assistant.
Use ONLY the provided PDF context to answer.

Context:
{context_str}

Chat History:
{history_text}

Question:
{question}

Answer based on the context only.
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error from Gemini: {str(e)}"
