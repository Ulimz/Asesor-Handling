from fastapi import APIRouter
from pydantic import BaseModel

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

@router.post("/nomina", response_model=NominaOutput)
def calcular_nomina(data: NominaInput):
    from app.services.legal_engine import legal_engine
    result = legal_engine.calculate_payroll(data.gross_annual_salary, data.age, data.payments)
    return result
