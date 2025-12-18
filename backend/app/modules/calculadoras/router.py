from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import SalaryConceptDefinition, SalaryTable
from app.schemas.salary import CalculationRequest, SalaryResponse
from app.services.calculator_service import CalculatorService

router = APIRouter(prefix="/calculadoras", tags=["calculadoras"])

class NominaInput(BaseModel):
    gross_annual_salary: float
    age: int = 30
    payments: int = 12  # 12 or 14

class NominaOutput(BaseModel):
    gross_monthly: float
    net_monthly: float
    irpf_percentage: float
    irpf_amount: float
    social_security_amount: float
    annual_net: float

class ConceptSchema(BaseModel):
    name: str
    code: str
    description: str | None
    input_type: str
    default_price: float
    level_values: dict | None = None

@router.get("/metadata/companies", response_model=List[str])
def get_companies(db: Session = Depends(get_db)):
    """Retorna lista de empresas disponibles"""
    companies = db.query(SalaryTable.company_id).distinct().all()
    # companies is a list of tuples like [('iberia',), ('groundforce',)]
    return [c[0] for c in companies if c[0] and c[0] != "convenio-sector"]

@router.get("/metadata/{company_id}/groups", response_model=List[str])
def get_company_groups(company_id: str, db: Session = Depends(get_db)):
    """Retorna grupos laborales únicos para una empresa"""
    groups = db.query(SalaryTable.group).filter(
        SalaryTable.company_id == company_id
    ).distinct().all()
    return sorted([g[0] for g in groups if g[0]])

@router.get("/metadata/{company_id}/{group_id}/levels", response_model=List[str])
def get_group_levels(company_id: str, group_id: str, db: Session = Depends(get_db)):
    """Retorna niveles únicos para un grupo específico"""
    levels = db.query(SalaryTable.level).filter(
        SalaryTable.company_id == company_id,
        SalaryTable.group == group_id
    ).distinct().all()
    return sorted([l[0] for l in levels if l[0]])

@router.get("/concepts/{company_slug}", response_model=List[ConceptSchema])
def get_company_concepts(company_slug: str, db: Session = Depends(get_db)):
    """Devuelve los conceptos variables disponibles para una empresa"""
    
    # Mapping for Sector Agreement companies
    target_slug = company_slug
    if company_slug in ["jet2", "norwegian", "south"]:
        target_slug = "convenio-sector"
        
    concepts = db.query(SalaryConceptDefinition).filter(
        (SalaryConceptDefinition.company_slug == target_slug) | (SalaryConceptDefinition.company_slug == "global"),
        SalaryConceptDefinition.is_active == True
    ).all()
    
    return [
        ConceptSchema(
            name=c.name,
            code=c.code,
            description=c.description,
            input_type=c.input_type,
            default_price=c.default_price or 0.0,
            level_values=c.level_values
        ) for c in concepts
    ]

@router.post("/nomina", response_model=NominaOutput)
def calcular_nomina(data: NominaInput):
    from app.services.legal_engine import legal_engine
    result = legal_engine.calculate_payroll(data.gross_annual_salary, data.age, data.payments)
    return result

@router.post("/smart", response_model=SalaryResponse)
def calcular_nomina_inteligente(
    request: CalculationRequest, 
    db: Session = Depends(get_db)
):
    service = CalculatorService(db)
    return service.calculate_smart_salary(request)

# Temporary Endpoint for Production Seeding (User Self-Service)
@router.post("/seed/sector")
def seed_sector_definitions():
    import os
    from seed_concepts_definitions import seed_concepts
    
    template_path = os.path.join(os.getcwd(), 'app', '..', 'data', 'structure_templates', 'convenio_sector.json')
    try:
        # Resolving path relative to backend root where app runs
        # If running from /backend, it's backend/data/...
        # But inside docker container, likely /app/backend/data or similar?
        # Let's try standard relative path: "data/structure_templates/convenio_sector.json"
        
        # Robust path finding
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # base_dir is /app
        # data is in /app/data if copied, or ../data?
        # In Dockerfile: COPY backend /app. So data is at /app/data ?
        # Let's check where seed_concepts_definitions.py looks: os.path.join('backend', 'data'...)
        
        # We will try absolute path based on known structure
        real_path = os.path.join(os.getcwd(), "data", "structure_templates", "convenio_sector.json")
        if not os.path.exists(real_path):
             return {"status": "error", "message": f"Template not found at {real_path}"}
             
        seed_concepts(real_path)
        return {"status": "success", "message": "Sector definitions updated from template"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
