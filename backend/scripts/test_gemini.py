import os
from dotenv import load_dotenv
import sys

# Add backend directory to path (assuming script is in backend/scripts/)
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.append(backend_dir)

# Load env manually from backend root
env_path = os.path.join(backend_dir, ".env")
load_dotenv(env_path)

from app.services.rag_engine import RagEngine

def test_gemini():
    print("Testing Gemini Integration...")
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        print("❌ Error: GOOGLE_API_KEY not found in .env")
        return

    print(f"✅ Found API Key: {key[:5]}...")

    try:
        rag = RagEngine()
    except Exception as e:
        print(f"❌ Error initializing RagEngine: {e}")
        return

    if not rag.gen_model:
         print("❌ Error: RagEngine gen_model not initialized (check API key)")
         return

    print("✅ RagEngine initialized with Gemini")

    # Mock context
    context = [
        {"content": "El artículo 24 del Convenio Colectivo establece que los trabajadores tienen derecho a 22 días laborables de vacaciones anuales retribuidas."},
        {"content": "Las vacaciones se disfrutarán preferentemente en el periodo estival."}
    ]
    query = "¿Cuántos días de vacaciones tengo y cuándo puedo cogerlas?"

    print(f"\nQuery: {query}")
    print("Generating answer...")
    
    answer = rag.generate_answer(query, context)
    
    print("\n--- Answer ---")
    print(answer)
    print("----------------")
    
    if answer and not answer.startswith("Error"):
        print("✅ Test Passed: Answer generated successfully")
    else:
        print("❌ Test Failed: No clean answer generated")

if __name__ == "__main__":
    test_gemini()
