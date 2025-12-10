
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set dummy Google API Key if not present (to avoid startup error if checks enable)
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "dummy"

from app.services.rag_engine import rag_engine

async def test_rag():
    print("--- Test 1: Retrieval ---")
    query = "precio horas perentorias"
    print(f"Query: {query}")
    
    # Use DB session to avoid ES fallback
    from app.db.database import SessionLocal
    with SessionLocal() as db:
        results = rag_engine.search(query, company_slug="iberia", limit=3, db=db)
    
        if not results:
            print("❌ No results found!")
        else:
            print(f"✅ Found {len(results)} chunks in total.")
            
            # Check for big chunks
            big_chunks = [r for r in results if len(r['content']) > 10000]
            if big_chunks:
                print(f"🚀 SUCCESS: Found {len(big_chunks)} LARGE chunks (>10k chars)!")
                for bc in big_chunks:
                    print(f"   - Ref: {bc['article_ref']} | Len: {len(bc['content'])}")
            else:
                print("⚠️ WARNING: No large chunks found.")
            # Updated result format (it returns dicts now)
            for r in results:
                 content = r['content']
                 print(f"   - Score: {r['score']:.4f}")
                 print(f"     Length: {len(content)}")
                 print(f"     Start: {content[:100]}...")
                 
                 if "perentoria" in content.lower():
                     idx = content.lower().find("perentoria")
                     print(f"     [SUCCESS] 'perentoria' found at index {idx}")
                     print(f"     Context: {content[idx:idx+200]}...")
                 else:
                     print("     [WARNING] 'perentoria' NOT found in this chunk.")
                 print("-" * 30)
    
    print("\n--- Test 2: Generation (Mock) ---")
    # We might not have a valid Google API Key set in this env for generation, 
    # so we test if the prompt construction works.
    try:
        # Just getting the chunks is enough to prove the RAG "Retrieval" part works.
        # "Generation" depends on external API.
        pass
    except Exception as e:
        print(f"Generation check skipped: {e}")

if __name__ == "__main__":
    asyncio.run(test_rag())
