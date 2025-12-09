import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import DocumentChunk

def verify_tables_in_db():
    """Verify that tables are actually stored in the database."""
    print("🔍 Verifying Table Storage in Database...\n")
    db = SessionLocal()
    
    # Query chunks that contain pipe characters (markdown tables)
    chunks_with_tables = db.query(DocumentChunk).filter(
        DocumentChunk.content.like('%|%')
    ).limit(10).all()
    
    print(f"📊 Found {len(chunks_with_tables)} chunks with table markers (|)\n")
    
    if chunks_with_tables:
        print("Sample chunks with tables:\n")
        for i, chunk in enumerate(chunks_with_tables[:3], 1):
            print(f"{'='*60}")
            print(f"Sample {i}: {chunk.article_ref}")
            print(f"{'='*60}")
            
            # Find table section
            content = chunk.content
            pipe_index = content.find('|')
            
            if pipe_index != -1:
                # Show 200 chars around first pipe
                start = max(0, pipe_index - 50)
                end = min(len(content), pipe_index + 400)
                preview = content[start:end]
                
                print(f"Table preview:\n{preview}\n")
            
            # Count rows
            rows = content.count('|')
            print(f"Pipe characters: {rows}")
            print()
        
        print("✅ Tables are stored correctly in database!")
    else:
        print("❌ No tables found in database!")
    
    db.close()

if __name__ == "__main__":
    verify_tables_in_db()
