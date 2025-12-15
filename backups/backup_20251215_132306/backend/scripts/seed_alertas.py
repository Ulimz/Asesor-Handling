from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.modules.alertas.models import Alerta
from app.db.base import Base
from datetime import datetime, timedelta

# Asegurar tablas
Base.metadata.create_all(bind=engine)

def seed_alertas():
    db = SessionLocal()
    
    # Limpiar existentes opcionalmente
    # db.query(Alerta).delete()
    
    alertas_data = [
        {
            "title": "Nuevas Tablas Salariales 2024",
            "description": "Se ha publicado la revisión salarial del IPC + 1.5% para todos los grupos profesionales. Efectivo desde enero.",
            "type": "convenio",
            "created_at": datetime.now() - timedelta(days=2),
            "is_active": True
        },
        {
            "title": "Sentencia Tribunal Supremo: Pausas Visuales",
            "description": "Nueva jurisprudencia confirma el derecho a 5 min de pausa visual cada hora para puestos de check-in continuado.",
            "type": "jurisprudencia",
            "created_at": datetime.now() - timedelta(days=10),
            "is_active": True
        },
        {
            "title": "Recordatorio: Uso de EPIs en Pista",
            "description": "Debido a la auditoría de AESA, se recuerda la obligatoriedad del chaleco reflectante clase 2 en todas las zonas de rampa.",
            "type": "seguridad",
            "created_at": datetime.now() - timedelta(days=15),
            "is_active": True
        },
        {
            "title": "Reforma del Estatuto de los Trabajadores",
            "description": "Cambios en los permisos retribuidos. Se amplía el permiso por hospitalización a 5 días y se permite el teletrabajo por fuerza mayor.",
            "type": "reforma",
            "created_at": datetime.now() - timedelta(days=30),
            "is_active": True
        }
    ]

    count = 0
    for data in alertas_data:
        exists = db.query(Alerta).filter(Alerta.title == data["title"]).first()
        if not exists:
            alerta = Alerta(**data)
            db.add(alerta)
            count += 1
            print(f"➕ Alerta creada: {data['title']}")
    
    db.commit()
    db.close()
    print(f"✅ Seeding completado. {count} nuevas alertas.")

if __name__ == "__main__":
    seed_alertas()
