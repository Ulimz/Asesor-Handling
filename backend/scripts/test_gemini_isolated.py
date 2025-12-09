import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys

# Load env manually
load_dotenv(".env")

def test_gemini_isolated():
    print("Testing Gemini Integration (Isolated)...")
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        print("❌ Error: GOOGLE_API_KEY not found in .env")
        return

    print(f"✅ Found API Key: {key[:5]}...")

    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = "Eres un asistente de handling. Responde brevemente: ¿Qué es el handling?"
        print(f"\nPrompt: {prompt}")
        print("Generating...")
        
        response = model.generate_content(prompt)
        print(f"\n✅ Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_gemini_isolated()
