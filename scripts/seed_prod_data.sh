#!/bin/bash
# Script para poblar la base de datos de producción (Railway)
# Uso: ./seed_prod_data.sh

echo "🚀 Iniciando carga de datos en Producción..."

# 1. Verificar variables
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL no está definida."
    echo "   Por favor exporta la variable antes de ejecutar:"
    echo "   export DATABASE_URL='postgresql://...'"
    exit 1
fi

export PYTHONPATH=$PYTHONPATH:.

# 2. Inicializar DB (Tablas + pgvector)
echo "\n📦 Creando tablas y extensiones..."
python backend/scripts/init_db.py

# 3. Cargar Convenios (Datos Básicos)
echo "\n📄 Cargando Convenios..."
python backend/seed_convenios.py

# 4. Cargar XMLs y generar Vectores
echo "\n🧠 Cargando Vectores (puede tardar)..."
# Asegurar que ejecutamos desde la raíz para que encuentre backend/data
python backend/run_seed_cloud_vectors.py

echo "\n✅ Proceso completado."
