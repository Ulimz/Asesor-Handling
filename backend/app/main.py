from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.usuarios.router import router as usuarios_router
from app.modules.empresas.router import router as empresas_router
from app.modules.convenios.router import router as convenios_router
from app.modules.articulos.router import router as articulos_router
from app.modules.jurisprudencia.router import router as jurisprudencia_router
from app.modules.reclamaciones.router import router as reclamaciones_router
from app.modules.calculadoras.router import router as calculadoras_router
from app.modules.alertas.router import router as alertas_router
from app.modules.ia.router import router as ia_router
from app.modules.articulos.search_router import router as articulos_search_router
from app.modules.admin.router import router as admin_router


from app.db.database import engine
from app.db.base import Base
# Importar modelos para que Base los reconozca en create_all
from app.db import models
from app.modules.usuarios import models as user_models

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Auto-migration: Check and patch missing columns (Schema Drift)
from app.db.schema_patch import patch_database
patch_database()

app = FastAPI(title="Asistente Handling API", description="Backend legal modular para el sector handling aeroportuario español.")

# Configuración CORS segura
# Configuración CORS segura
origins = [
    "http://localhost:3000",
    "http://localhost:3002",
    "https://asesor-handling-production.up.railway.app",
    "https://asistentehandling.es",
    "https://www.asistentehandling.es",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Abrir temporalmente para debug de conectividad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(usuarios_router, prefix="/api")
app.include_router(empresas_router, prefix="/api")
app.include_router(convenios_router, prefix="/api")
app.include_router(articulos_router, prefix="/api")
app.include_router(jurisprudencia_router, prefix="/api")
app.include_router(reclamaciones_router, prefix="/api")
app.include_router(calculadoras_router, prefix="/api")
app.include_router(alertas_router, prefix="/api")
app.include_router(ia_router, prefix="/api")
app.include_router(articulos_search_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

@app.get("/")
def read_root():
    return {"msg": "API Asistente Handling funcionando"}
