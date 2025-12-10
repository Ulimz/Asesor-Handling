from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import SalaryConceptDefinition
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

@router.get("/concepts/{company_slug}", response_model=List[ConceptSchema])
def get_company_concepts(company_slug: str, db: Session = Depends(get_db)):
    """Devuelve los conceptos variables disponibles para una empresa"""
    concepts = db.query(SalaryConceptDefinition).filter(
        SalaryConceptDefinition.company_slug == company_slug,
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
