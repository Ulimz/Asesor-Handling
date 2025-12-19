
import os
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv()

from app.db.models import SalaryConceptDefinition, SalaryTable, LegalDocument

def backup_azul():
    print("💾 BACKING UP AZUL HANDLING DATA...")
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ No DATABASE_URL")
        return
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    company_slug = "azul-handling"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(os.getcwd(), 'backend', 'backups', f'azul_backup_{timestamp}.json')
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    
    data = {
        "metadata": {
            "company": company_slug,
            "timestamp": timestamp,
            "version": "Shielded 1.0"
        },
        "concepts": [],
        "salary_tables": [],
        "documents": [] # Storing metadata only, chunks are heavy and re-ingestable
    }
    
    try:
        # 1. Salary Concepts (Definitions)
        print("   Collecting Salary Concepts...")
        concepts = db.query(SalaryConceptDefinition).filter(SalaryConceptDefinition.company_slug == company_slug).all()
        for c in concepts:
            data["concepts"].append({
                "code": c.code,
                "name": c.name,
                "default_price": c.default_price,
                "input_type": c.input_type,
                "level_values": c.level_values,
                "has_tiers": False, # Flattened in DB
                "description": c.description
            })
            
        # 2. Salary Tables (Base Salary)
        print("   Collecting Salary Tables...")
        tables = db.query(SalaryTable).filter(SalaryTable.company_id == company_slug).all()
        for t in tables:
            data["salary_tables"].append({
                "year": t.year,
                "group": t.group,
                "level": t.level,
                "concept": t.concept,
                "amount": t.amount
            })
            
        # 3. Documents
        print("   Collecting Document Metadata...")
        docs = db.query(LegalDocument).filter(LegalDocument.company == company_slug).all()
        for d in docs:
            data["documents"].append({
                "id": d.id,
                "title": d.title,
                "category": d.category
            })

        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Backup saved to: {backup_path}")
        print(f"   - {len(data['concepts'])} concepts")
        print(f"   - {len(data['salary_tables'])} table rows")
        print(f"   - {len(data['documents'])} documents")
        
    except Exception as e:
        print(f"❌ Backup Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    backup_azul()
