import sys
import os
import google.generativeai as genai
from sqlalchemy import select

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import DocumentChunk
from dotenv import load_dotenv

load_dotenv()

def verify_generation():
    print("🧠 Verifying LLM Generation Quality with Messy Data...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ SKIPPING: No GOOGLE_API_KEY found.")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    db = SessionLocal()
    try:
        # 1. Fetch the messy ANEXO I chunk
        stmt = select(DocumentChunk).where(DocumentChunk.article_ref.ilike("%ANEXO I%")).limit(1)
        chunk = db.execute(stmt).scalars().first()
        
        if not chunk:
            print("❌ No ANEXO I found to test.")
            return

        messy_text = chunk.content
        print(f"📄 Retrieved Messy Text (len {len(messy_text)})...")

        # 2. Ask specific questions
        questions = [
            "¿Cuál es el salario base de un Agente Administrativo Nivel 2 en 2024?",
            "¿Cuánto cobra un Gestor en 2024?",
            "Identifica las tablas salariales y dime si hay columnas por año."
        ]

        for q in questions:
            print(f"\n❓ Question: {q}")
            prompt = f"""CONTEXTO:
{messy_text}

PREGUNTA:
{q}

Responde solo con el dato si lo encuentras, o 'NO ENCONTRADO'."""
            
            response = model.generate_content(prompt)
            print(f"🤖 Answer: {response.text.strip()}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_generation()
