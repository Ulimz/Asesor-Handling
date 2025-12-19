#!/usr/bin/env python3
"""
Add role column to users table
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv()

def add_role_column():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ No DATABASE_URL")
        return
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='role'
            """))
            
            if result.fetchone():
                print("✅ Column 'role' already exists")
                return
            
            # Add column
            print("🔧 Adding 'role' column to users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user'"))
            conn.commit()
            print("✅ Column 'role' added successfully")
            
            # Update existing superusers to admin role
            print("🔧 Updating superusers to admin role...")
            conn.execute(text("UPDATE users SET role = 'admin' WHERE is_superuser = true"))
            conn.commit()
            print("✅ Superusers updated to admin role")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_role_column()
