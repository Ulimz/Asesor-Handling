from fastapi import APIRouter, Query
from app.services.elasticsearch_service import search_documents

router = APIRouter(prefix="/articulos/search", tags=["articulos_search"])

@router.get("/")
def search_articulos(q: str = Query(..., description="Consulta semántica")):
    results = search_documents(index="articulos", query=q)
    return {"results": results}
