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
    concepts = db.query(SalaryConceptDefinition).filter(
        (SalaryConceptDefinition.company_slug == company_slug) | (SalaryConceptDefinition.company_slug == "global"),
        SalaryConceptDefinition.is_active == True
    ).all()
    
    return [
        ConceptSchema(
            name=c.name,
            code=c.code,
            description=c.description,
            input_type=c.input_type,
            default_price=c.default_price or 0.0
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
