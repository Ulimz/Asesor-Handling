
import os
import sys
import asyncio
from sqlalchemy import text
from app.database import engine, result_session
from app.models import Compania, Documento, Seccion, Articulo

# Este script asume que la CONNECTION STRING en tus variables de entorno (.env) 
# apunta a la Base de Datos de PRODUCCIÓN (Supabase) temporalmente.

async def seed_prod_data():
    print("🚀 Iniciando migración de datos a PRODUCCIÓN...")
    
    # 1. Verificar conexión
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Conexión establecida con la BD.")
    except Exception as e:
        print(f"❌ Error conectando a la BD: {e}")
        return

    # 2. Aquí podrías añadir lógica para leer tus JSON locales y subirlos
    # pero dado que ya tienes 'init_db_resources.py' que lee Iberia.json,
    # lo mejor es simplemente recomendar usar ese mismo script.
    
    print("\nℹ️  INSTRUCCIONES:")
    print("Para poblar la base de datos de producción:")
    print("1. Ejecuta 'python init_db_resources.py' (asegura que .env apunta a Supabase).")
    print("2. Esto creará las tablas y cargará los datos de 'data/iberia.json'.")
    print("\nSi tienes más convenios en otros JSON, asegúrate de que el script los incluya.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_prod_data())
