from app.db.base import Base
from app.db.database import engine, SessionLocal
from app.modules.convenios.models import Convenio
from sqlalchemy.orm import Session

from sqlalchemy import text

# Limpiar tabla convenios (y dependencias) para aplicar nuevo esquema
with engine.connect() as connection:
    connection.execute(text("DROP TABLE IF EXISTS convenios CASCADE"))
    connection.commit()

# Re-crear tablas (solo las que faltan)
Base.metadata.create_all(bind=engine)

def seed_convenios():
    db: Session = SessionLocal()
    
    companies_data = [
        {"slug": "azul", "name": "Azul Handling", "description": "Convenio Colectivo Azul Handling", "color": "#004481"},
        {"slug": "iberia", "name": "Iberia", "description": "Convenio Colectivo Iberia Tierra", "color": "#D7192D"},
        {"slug": "groundforce", "name": "Groundforce", "description": "Convenio Groundforce Globalia", "color": "#0033A0"},
        {"slug": "swissport", "name": "Swissport", "description": "Convenio Colectivo Swissport", "color": "#FF6600"},
        {"slug": "menzies", "name": "Menzies", "description": "Convenio Menzies Aviation", "color": "#2B3E50"},
        {"slug": "wfs", "name": "WFS", "description": "Convenio Worldwide Flight Services", "color": "#E31837"},
    ]

    print("🌱 Seeding Convenios...")
    for data in companies_data:
        existing = db.query(Convenio).filter(Convenio.slug == data["slug"]).first()
        if not existing:
            convenio = Convenio(**data)
            db.add(convenio)
            print(f"   Created: {data['name']}")
        else:
            print(f"   Skipped (Exists): {data['name']}")
    
    db.commit()
    db.close()
    print("✅ Seeding Complete!")

if __name__ == "__main__":
    seed_convenios()
