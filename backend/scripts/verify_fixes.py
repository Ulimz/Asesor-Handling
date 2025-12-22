import sys
import os
import logging

# Set up path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.rag_engine import rag_engine
from app.db.database import SessionLocal
from app.db.models import DocumentChunk
from sqlalchemy import text

def verify_fixes():
    print("\n" + "="*60)
    print("🕵️‍♂️ FINAL FIX VERIFICATION SUITE")
    print("="*60)
    
    # TEST 1: Unblocked Gatekeeper
    print("\n[TEST 1] RAG Gatekeeper (Simple Queries)")
    queries = [
        "cuanto cobra el nivel 3", 
        "diferencia nivel 1 y 2", # Original comparison
        "cual es el sueldo base nivel 5"
    ]
    
    all_passed = True
    for q in queries:
        is_calc = rag_engine._is_calculation_query(q)
        status = "✅ PASS" if is_calc else "❌ FAIL"
        if not is_calc: all_passed = False
        print(f"Query: '{q}' -> is_calculation: {is_calc} {status}")
        
    if all_passed:
        print(">> GATEKEEPER FIX: SUCCESS")
    else:
        print(">> GATEKEEPER FIX: FAILED")

    # TEST 2: Ingestion Metadata
    print("\n[TEST 2] Ingestion Metadata (DB Check)")
    try:
        db = SessionLocal()
        # Count chunks with metadata->is_primary = 'true'
        # Note: metadata is JSONB in Postgres, usually accessed via operators, 
        # but here we can just fetch some and check in python to be safe and DB-agnostic for the script
        
        chunks = db.query(DocumentChunk).all() # Scan all to be sure
        tables_found = 0
        primary_found = 0
        metadata_populated = 0
        
        print(f"Total Chunks Scanned: {len(chunks)}")
        
        for c in chunks:
            meta = c.chunk_metadata
            if meta:
                metadata_populated += 1
                if meta.get('type') == 'table':
                    tables_found += 1
                if meta.get('is_primary') == 'true':
                    primary_found += 1
                    
        print(f"Metadata Populated: {metadata_populated}")
        print(f"Tables Detected: {tables_found}")
        print(f"Primary Anchors: {primary_found}")
        
        if primary_found > 0 and tables_found > 0:
            print(">> INGESTION FIX: SUCCESS")
        else:
             print(">> INGESTION FIX: FAILED (No primary anchors found)")
             
        db.close()
    except Exception as e:
        print(f"❌ DB Error: {e}")

if __name__ == "__main__":
    verify_fixes()
