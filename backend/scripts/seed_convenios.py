from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.modules.convenios.models import Convenio

def seed_convenios(db: Session = None):
    # If no session provided (local run), create one
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
    
    try:
        companies = [
            {"slug": "iberia", "name": "Iberia", "description": "Convenio Colectivo Iberia Handling", "color": "#D7192D"},
            {"slug": "azul", "name": "Azul Handling", "description": "Convenio Colectivo Azul Handling", "color": "#00AEEF"},
            {"slug": "groundforce", "name": "Groundforce", "description": "Convenio Groundforce", "color": "#003F7D"},
            {"slug": "swissport", "name": "Swissport", "description": "Convenio Swissport", "color": "#D50032"},
            {"slug": "menzies", "name": "Menzies", "description": "Convenio Menzies Aviation", "color": "#FFC72C"},
            {"slug": "wfs", "name": "WFS", "description": "Convenio WFS", "color": "#0055A4"},
            {"slug": "aviapartner", "name": "Aviapartner", "description": "Convenio Aviapartner", "color": "#8CC63F"},
            {"slug": "easyjet", "name": "EasyJet", "description": "Convenio EasyJet Handling", "color": "#FF6600"},
            {"slug": "south", "name": "South", "description": "South (Aplica Convenio Sector)", "color": "#E11D48"},
            {"slug": "jet2", "name": "Jet2.com", "description": "Jet2 (Aplica Convenio Sector)", "color": "#D7192D"},
            {"slug": "norwegian", "name": "Norwegian", "description": "Norwegian (Aplica Convenio Sector)", "color": "#B00000"},
        ]

        for company in companies:
            existing = db.query(Convenio).filter(Convenio.slug == company["slug"]).first()
            if not existing:
                print(f"Adding {company['name']}...")
                db_item = Convenio(
                    slug=company["slug"],
                    name=company["name"],
                    description=company["description"],
                    color=company["color"],
                    is_active=True
                )
                db.add(db_item)
            else:
                print(f"Skipping {company['name']} (already exists)")
        
        db.commit()
        print("Done seeding convenios.")
    finally:
        if should_close:
            db.close()

if __name__ == "__main__":
    seed_convenios()
