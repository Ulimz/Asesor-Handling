"""
Migration: Add updated_at and version columns to legal_documents table
Date: 2025-12-10
Reason: Data Integrity & Versioning
"""

import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine
from sqlalchemy import text

def upgrade():
    """Add updated_at and version columns"""
    print("🔧 Adding updated_at and version columns to legal_documents...")
    
    with engine.connect() as conn:
        # Check if columns already exist
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='legal_documents' AND column_name='updated_at'
        """)
        
        result = conn.execute(check_query)
        exists = result.fetchone() is not None
        
        if exists:
            print("   ℹ️ Columns already exist, skipping...")
            return
        
        # Add columns
        # We set default values to avoid nulls in existing records
        conn.execute(text("""
            ALTER TABLE legal_documents 
            ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
            ADD COLUMN version VARCHAR DEFAULT '1.0'
        """))
        
        conn.commit()
        
        print("   ✅ Columns added successfully!")

def downgrade():
    """Remove updated_at and version columns"""
    print("🔧 Removing updated_at and version columns...")
    
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE legal_documents 
            DROP COLUMN IF EXISTS updated_at,
            DROP COLUMN IF EXISTS version
        """))
        
        conn.commit()
        
        print("   ✅ Columns removed successfully!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration for versioning columns')
    parser.add_argument('action', choices=['upgrade', 'downgrade'], 
                       help='Migration action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'upgrade':
        upgrade()
    else:
        downgrade()
