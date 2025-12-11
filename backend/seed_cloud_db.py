import os
import sys
from sqlalchemy import create_engine, text
# Importar modelos para que se registren en metadata
from app.db.base import Base
from app.modules.usuarios import models as user_models
from app.modules.empresas import models as company_models
from app.modules.convenios import models as convenio_models
from app.modules.articulos import models as articulo_models
# ... otros modelos según necesidad (calculadora, alertas, etc)

# Scripts de carga de datos
from scripts.seed_convenios import seed_convenios

def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL no encontrada en variables de entorno.")
        print("   Asegúrate de editar el .env o .env.production con la URL de Railway.")
        return

    print(f"🔄 Conectando a Base de Datos Nube (URL empieza por {database_url[:20]}...)...")
    
    try:
        engine = create_engine(database_url)
        
        # 1. Validar conexión y activar pgvector
        with engine.connect() as connection:
            print("   ✅ Conexión exitosa.")
            print("   🔌 Activando extensión vector...")
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            connection.commit()
            
        # 2. Crear Tablas (Schema)
        print("   🏗️ Creando tablas (si no existen)...")
        Base.metadata.create_all(bind=engine)
        print("   ✅ Tablas creadas.")
        
        # 3. Seed de Datos (Convenios)
        # Necesitamos una sesión para los scripts de seed
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("   🌱 Ejecutando Seed de Convenios...")
        # Llama a tu función existente de seed
        # Nota: Asegúrate de que seed_convenios_sector acepte 'db'
        seed_convenios(db)
        
        db.close()
        print("✅ PROCESO COMPLETADO EXITOSAMENTE.")

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")

if __name__ == "__main__":
    main()
