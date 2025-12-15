"""
Migration: Add index to article_ref column in document_chunks table
Date: 2025-12-09
Reason: Performance optimization - faster lookups by article reference
"""

import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal, engine
from sqlalchemy import text

def upgrade():
    """Add index to article_ref column"""
    print("🔧 Adding index to article_ref column...")
    
    with engine.connect() as conn:
        # Check if index already exists
        check_query = text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'document_chunks' 
            AND indexname = 'ix_document_chunks_article_ref'
        """)
        
        result = conn.execute(check_query)
        exists = result.fetchone() is not None
        
        if exists:
            print("   ℹ️ Index already exists, skipping...")
            return
        
        # Create index
        create_index_query = text("""
            CREATE INDEX ix_document_chunks_article_ref 
            ON document_chunks (article_ref)
        """)
        
        conn.execute(create_index_query)
        conn.commit()
        
        print("   ✅ Index created successfully!")

def downgrade():
    """Remove index from article_ref column"""
    print("🔧 Removing index from article_ref column...")
    
    with engine.connect() as conn:
        drop_index_query = text("""
            DROP INDEX IF EXISTS ix_document_chunks_article_ref
        """)
        
        conn.execute(drop_index_query)
        conn.commit()
        
        print("   ✅ Index removed successfully!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration for article_ref index')
    parser.add_argument('action', choices=['upgrade', 'downgrade'], 
                       help='Migration action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'upgrade':
        upgrade()
    else:
        downgrade()
