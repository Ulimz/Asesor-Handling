from sqlalchemy.orm import Session
from app.db.models import SalaryTable, SalaryConceptDefinition
from app.schemas.salary import CalculationRequest, SalaryResponse, SalaryConcept

class CalculatorService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_smart_salary(self, request: CalculationRequest) -> SalaryResponse:
        """
        Calcula la nómina basada en el perfil del usuario (Company, Group, Level)
        y los inputs variables (Dinámicos + Legacy)
        """
        
        # --- DEFINICIÓN DE TABLAS SALARIALES 2025 (Hardcoded por ahora) ---
        # Structure: Group -> Level -> { ConceptCode: Price }
        # BASE_ANNUAL: Salario Bruto Anual de Tablas (se dividirá entre 14 pagas)
        salary_tables_2025 = {
            "Serv. Auxiliares": {
                "Nivel entrada": {"BASE_ANNUAL": 18450.87, "HORA_EXTRA": 16.17, "HORA_PERENT": 18.86, "HC_ESPECIAL": 18.30},
                "Nivel 2":       {"BASE_ANNUAL": 21850.75, "HORA_EXTRA": 19.14, "HORA_PERENT": 22.34, "HC_ESPECIAL": 21.67},
                "Nivel 3":       {"BASE_ANNUAL": 22507.75, "HORA_EXTRA": 19.72, "HORA_PERENT": 23.01, "HC_ESPECIAL": 22.32},
                "Nivel 4":       {"BASE_ANNUAL": 22957.90, "HORA_EXTRA": 20.11, "HORA_PERENT": 23.47, "HC_ESPECIAL": 22.77},
                "Nivel 5":       {"BASE_ANNUAL": 23408.06, "HORA_EXTRA": 20.51, "HORA_PERENT": 23.93, "HC_ESPECIAL": 23.22},
                "Nivel 6":       {"BASE_ANNUAL": 24344.38, "HORA_EXTRA": 21.33, "HORA_PERENT": 24.88, "HC_ESPECIAL": 24.15},
                "Nivel 7":       {"BASE_ANNUAL": 25318.15, "HORA_EXTRA": 22.18, "HORA_PERENT": 25.88, "HC_ESPECIAL": 25.11},
            },
            "Administrativos": {
                "Nivel entrada": {"BASE_ANNUAL": 18632.39, "HORA_EXTRA": 16.33, "HORA_PERENT": 19.05, "HC_ESPECIAL": 18.48},
                "Nivel 2":       {"BASE_ANNUAL": 22065.51, "HORA_EXTRA": 19.33, "HORA_PERENT": 22.56, "HC_ESPECIAL": 21.89},
                "Nivel 3":       {"BASE_ANNUAL": 22728.97, "HORA_EXTRA": 19.91, "HORA_PERENT": 23.23, "HC_ESPECIAL": 22.54},
                "Nivel 4":       {"BASE_ANNUAL": 23183.55, "HORA_EXTRA": 20.31, "HORA_PERENT": 23.70, "HC_ESPECIAL": 22.99},
                "Nivel 5":       {"BASE_ANNUAL": 23638.13, "HORA_EXTRA": 20.71, "HORA_PERENT": 24.16, "HC_ESPECIAL": 23.44},
                "Nivel 6":       {"BASE_ANNUAL": 24583.65, "HORA_EXTRA": 21.54, "HORA_PERENT": 25.13, "HC_ESPECIAL": 24.38},
                "Nivel 7":       {"BASE_ANNUAL": 25567.00, "HORA_EXTRA": 22.40, "HORA_PERENT": 26.13, "HC_ESPECIAL": 25.36},
            },
            "Técnicos gestores": {
                "Nivel entrada": {"BASE_ANNUAL": 28460.70, "HORA_EXTRA": 24.94, "HORA_PERENT": 29.09, "HC_ESPECIAL": 28.23},
                "Nivel 2":       {"BASE_ANNUAL": 28516.35, "HORA_EXTRA": 24.99, "HORA_PERENT": 29.15, "HC_ESPECIAL": 28.28},
                "Nivel 3":       {"BASE_ANNUAL": 29367.68, "HORA_EXTRA": 25.73, "HORA_PERENT": 30.02, "HC_ESPECIAL": 29.13},
                "Nivel 4":       {"BASE_ANNUAL": 29955.04, "HORA_EXTRA": 26.25, "HORA_PERENT": 30.62, "HC_ESPECIAL": 29.71},
                "Nivel 5":       {"BASE_ANNUAL": 30542.39, "HORA_EXTRA": 26.76, "HORA_PERENT": 31.22, "HC_ESPECIAL": 30.29},
                "Nivel 6":       {"BASE_ANNUAL": 31764.09, "HORA_EXTRA": 27.83, "HORA_PERENT": 32.47, "HC_ESPECIAL": 31.50},
                "Nivel 7":       {"BASE_ANNUAL": 33034.65, "HORA_EXTRA": 28.94, "HORA_PERENT": 33.77, "HC_ESPECIAL": 32.76},
            }
        }
        
        # 1. Lookup Pricing based on Request Profile
        user_group = request.user_group if request.user_group in salary_tables_2025 else "Serv. Auxiliares"
        user_level = request.user_level if request.user_level else "Nivel entrada"
        
        group_data = salary_tables_2025.get(user_group, salary_tables_2025["Serv. Auxiliares"])
        active_prices = group_data.get(user_level)

        # Fallback partial match lookup
        if not active_prices:
             # Try case-insensitive matching
             for key, data in group_data.items():
                 if user_level.lower() in key.lower():
                     active_prices = data
                     break
        
        if not active_prices: 
            # Ultimate fallback
            active_prices = group_data.get("Nivel entrada", {})

        # 2. Base Salary Calculation
        # Annual base from table / Payments (14)
        annual_table_salary = active_prices.get("BASE_ANNUAL", 18450.87)
        
        # LOGIC CHANGE: Base monthly is ALWAYS Annual / 14 (standard monthly payment)
        full_base_monthly = annual_table_salary / 14.0
        
        # Apply Contract Percentage (Pro-rata)
        prorata_factor = request.contract_percentage / 100.0
        
        base_salary = full_base_monthly * prorata_factor
        
        # Assume Convenience and Transport are included in the gross table salary or are 0 for this simplified view
        plus_convenio = 0.0 
        plus_transporte = 0.0

        # 3. Concepts List Population
        concepts = []
        concepts.append(SalaryConcept(name="Salario Base (Parte Proporcional)", amount=base_salary, type="devengo"))
        
        # --- PRORATA LOGIC SEPARATION ---
        # If user selected 12 payments, we add specific concept "Prorrata Pagas Extra"
        # Prorata Amount = (Annual / 14) * 2 / 12  -> (Standard Month * 2 Extras) / 12 Months
        if request.payments == 12:
            prorata_extras_total = (annual_table_salary * 2 / 14.0) * prorata_factor # Total extra pay for the year adjusted by contract %
            prorata_monthly_concept = prorata_extras_total / 12.0
            
            concepts.append(SalaryConcept(name="Prorrata Pagas Extra", amount=prorata_monthly_concept, type="devengo"))
            
            # Update base for total calculation (Base + Prorata)
            # CAREFUL: "base_salary" variable keeps tracking just the base. We add to gross later.
            base_salary_for_gross = base_salary + prorata_monthly_concept
        else:
            base_salary_for_gross = base_salary
        
        total_variable = 0
        
        # --- DYNAMIC CONCEPT LOGIC ---
        # Fetch definitions from DB for this company
        db_concepts = self.db.query(SalaryConceptDefinition).filter(
            SalaryConceptDefinition.company_slug == request.company_slug,
            SalaryConceptDefinition.is_active == True
        ).all()
        
        start_concept_map = {c.code: c for c in db_concepts}
        
        # Process Dynamic Variables from Request
        if request.dynamic_variables:
            for code, input_val in request.dynamic_variables.items():
                if input_val > 0 and code in start_concept_map:
                    definition = start_concept_map[code]
                    unit_price = definition.default_price or 0.0 # Default from DB
                    
                    # OVERRIDE: Apply Level-Based Scaling for specific concepts
                    if code in ["HORA_EXTRA", "HC_ESPECIAL", "HORA_PERENT"]:
                        if code in active_prices:
                            unit_price = active_prices[code]
                    
                    amount = input_val * unit_price
                    concepts.append(SalaryConcept(
                        name=definition.name,
                        amount=amount,
                        type="devengo"
                    ))
                    total_variable += amount

        # --- LEGACY FALLBACKS REMOVED OR SIMPLIFIED ---
        # Not computing legacy night hours if not in dynamic vars, assuming DB definitions handle it.

        # Totales
        gross_monthly = base_salary_for_gross + total_variable
        
        # Deductions
        # 1. Seguridad Social (Detailed)
        base_cotizacion = gross_monthly 
        
        rate_cc = 0.047
        rate_fp = 0.001
        rate_unemployment = 0.0160 if request.contract_type == "temporal" else 0.0155
        
        val_cc = base_cotizacion * rate_cc
        val_unemployment = base_cotizacion * rate_unemployment
        val_fp = base_cotizacion * rate_fp
        
        total_ss_deduction = val_cc + val_unemployment + val_fp
        
        # 2. IRPF (Voluntary/Dynamic)
        irpf_rate = (request.irpf_percentage / 100.0) if request.irpf_percentage is not None else 0.15 
        irpf_deduction = gross_monthly * irpf_rate
        
        total_deductions = total_ss_deduction + irpf_deduction
        net_monthly = gross_monthly - total_deductions
        
        # Add Deduction Concepts
        concepts.append(SalaryConcept(name=f"SS: Contingencias Comunes (4.70%)", amount=-val_cc, type="deduccion"))
        concepts.append(SalaryConcept(name=f"SS: Desempleo ({rate_unemployment*100:.2f}%)", amount=-val_unemployment, type="deduccion"))
        concepts.append(SalaryConcept(name=f"SS: Formación Profesional (0.10%)", amount=-val_fp, type="deduccion"))
        concepts.append(SalaryConcept(name=f"Retención IRPF ({irpf_rate*100:.1f}%)", amount=-irpf_deduction, type="deduccion"))
        
        # Calculate Estimated Annual Gross using the TABLE annual value + annualized variables
        annual_gross_est = annual_table_salary * prorata_factor + (total_variable * 12) # Approximate

        return SalaryResponse(
            base_salary_monthly=round(base_salary, 2),
            variable_salary=round(total_variable, 2),
            gross_monthly_total=round(gross_monthly, 2),
            net_salary_monthly=round(net_monthly, 2),
            breakdown=concepts,
            annual_gross=round(annual_gross_est, 2)
        )

