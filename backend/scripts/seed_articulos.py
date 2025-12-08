import json
import os
from app.services.elasticsearch_service import index_document, es

# Definir mappings para el índice "articulos"
MAPPING = {
    "mappings": {
        "properties": {
            "title": {"type": "text", "analyzer": "spanish"},
            "content": {"type": "text", "analyzer": "spanish"},
            "tags": {"type": "keyword"},
            "company_slug": {"type": "keyword"},
            "scope": {"type": "keyword"} 
        }
    }
}

def seed_elasticsearch():
    print("🚀 Iniciando indexación en Elasticsearch...")
    
    # 1. Crear índice si no existe
    if not es.indices.exists(index="articulos"):
        es.indices.create(index="articulos", body=MAPPING)
        print("✅ Índice 'articulos' creado.")
    else:
        # Opcional: Borrar y recrear para asegurar limpieza
        es.indices.delete(index="articulos")
        es.indices.create(index="articulos", body=MAPPING)
        print("♻️ Índice 'articulos' recreado.")

    # 2. Cargar datos de los archivos JSON del frontend (hardcoded paths por ahora para migración)
    # Asumimos que el script corre desde root o backend, ajustamos paths.
    BASE_PATH = "../src/data/documents"
    
    files = [
        {"file": "global-estatuto.json", "scope": "global", "company_slug": None},
        {"file": "company-azul.json", "scope": "company", "company_slug": "azul"},
        {"file": "company-iberia.json", "scope": "company", "company_slug": "iberia"},
        {"file": "company-groundforce.json", "scope": "company", "company_slug": "groundforce"},
    ]

    count = 0
    for item in files:
        path = os.path.join(BASE_PATH, item["file"])
        if not os.path.exists(path):
            print(f"⚠️ Archivo no encontrado: {path}")
            continue
            
        with open(path, "r", encoding="utf-8") as f:
            docs = json.load(f)
            
        for doc in docs:
            doc_body = {
                "title": doc["title"],
                "content": doc["content"],
                "tags": doc.get("tags", []),
                "scope": item["scope"],
                "company_slug": item["company_slug"]
            }
            # Usamos el ID del json si existe, o generamos uno
            doc_id = doc.get("id")
            
            index_document(index="articulos", doc_id=doc_id, body=doc_body)
            count += 1
            print(f"   Indexed: {doc['title'][:30]}...")

    print(f"🎉 Indexación completada. Total documentos: {count}")

if __name__ == "__main__":
    seed_elasticsearch()
