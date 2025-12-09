import sys
import os
sys.path.append('/app')
from app.db.database import SessionLocal
from app.db.models import LegalDocument, DocumentChunk
import sys

def inspect_chunk(chunk_id):
    db = SessionLocal()
    try:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if chunk:
            print(f"--- CHUNK {chunk_id} Content ---")
            print(chunk.content)
            print("--- END CHUNK ---")
        else:
            print("Chunk not found")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_chunk(201)
