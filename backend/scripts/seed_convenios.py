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
        {"slug": "iberia", "name": "South (antes Iberia)", "description": "Convenio Colectivo South (ex-Iberia)", "color": "#D7192D"},
        {"slug": "groundforce", "name": "Groundforce", "description": "Convenio Groundforce Globalia", "color": "#0033A0"},
        {"slug": "swissport", "name": "Swissport", "description": "Convenio Colectivo Swissport", "color": "#FF6600"},
        {"slug": "menzies", "name": "Menzies", "description": "Convenio Menzies Aviation", "color": "#2B3E50"},
        {"slug": "wfs", "name": "WFS", "description": "Convenio Worldwide Flight Services", "color": "#E31837"},
        {"slug": "aviapartner", "name": "Aviapartner", "description": "Convenio Colectivo Aviapartner", "color": "#00965E"},
        {"slug": "easyjet", "name": "easyJet", "description": "Convenio Colectivo easyJet Handling", "color": "#FF6600"},
        {"slug": "general", "name": "V Convenio Sector", "description": "V Convenio Colectivo General del Sector", "color": "#64748b"},
    ]

    print("🌱 Seeding Convenios...")
    for data in companies_data:
        existing = db.query(Convenio).filter(Convenio.slug == data["slug"]).first()
        if not existing:
            convenio = Convenio(**data)
            db.add(convenio)
            print(f"   Created: {data['name']}")
        else:
            existing.name = data["name"]
            existing.description = data["description"]
            existing.color = data["color"]
            print(f"   Updated: {data['name']}")
    
    db.commit()
    db.close()
    # Sync logic: Remove companies not in the list
    allowed_slugs = [data["slug"] for data in companies_data]
    db.query(Convenio).filter(Convenio.slug.notin_(allowed_slugs)).delete(synchronize_session=False)

    print("✅ Seeding & Sync Complete!")

if __name__ == "__main__":
    seed_convenios()
