from pydantic import BaseModel
from typing import List, Optional

class SalaryConcept(BaseModel):
    name: str
    amount: float
    type: str # "devengo" o "deduccion"

class CalculationRequest(BaseModel):
    company_slug: str # "iberia"
    user_group: str # "Administrativos"
    user_level: str # "Nivel D" (o el que corresponda)
    
    # Conceptos Variables (User Input)
    # Deprecated specific fields (keeping for compatibility during migration)
    night_hours: Optional[float] = 0
    holiday_hours: Optional[float] = 0
    
    # Dynamic Variables (key=concept_code, value=input_amount)
    dynamic_variables: Optional[dict[str, float]] = {} 
    
    # Legacy fallbacks
    extra_hours: Optional[float] = 0 
    perentory_hours: Optional[float] = 0
    complementary_hours: Optional[float] = 0
    madrugues: Optional[int] = 0
    
    payments: int = 14 # 12 o 14 pagas
    age: Optional[int] = 30
    gross_annual_salary: Optional[float] = None
    
    # Contract Details
    contract_percentage: float = 100.0 # 100% = Full Time, 50% = Half Time
    contract_type: str = "indefinido" # "indefinido" (1.55% desempleo) or "temporal" (1.60%)
    
    # Tax Details
    irpf_percentage: Optional[float] = None # User provided retention (e.g. 15.0)

class SalaryResponse(BaseModel):
    base_salary_monthly: float
    variable_salary: float
    gross_monthly_total: float
    
    net_salary_monthly: float
    
    breakdown: List[SalaryConcept]
    
    annual_gross: float # Proyección
