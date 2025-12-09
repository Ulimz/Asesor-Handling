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


from app.db.database import engine
from app.db.base import Base
# Importar modelos para que Base los reconozca en create_all
from app.db import models

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Asistente Handling API", description="Backend legal modular para el sector handling aeroportuario español.")

# Configuración CORS segura
origins = [
    "https://tudominio.com",
    "http://localhost:3000",
    "http://localhost:3002",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(usuarios_router)
app.include_router(empresas_router)
app.include_router(convenios_router)
app.include_router(articulos_router)
app.include_router(jurisprudencia_router)
app.include_router(reclamaciones_router)
app.include_router(calculadoras_router)
app.include_router(alertas_router)
app.include_router(ia_router)
app.include_router(articulos_search_router)

@app.get("/")
def read_root():
    return {"msg": "API Asistente Handling funcionando"}
