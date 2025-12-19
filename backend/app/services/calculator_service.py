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
        
        # 1. Lookup Pricing from DB (Dynamic Multi-Company)
        user_group = request.user_group or "Serv. Auxiliares"
        user_level = request.user_level or "Nivel entrada"
        
        # Helper to fetch prices as a dict
        active_prices = self._get_salary_prices_from_db(request.company_slug, user_group, user_level)
        
        if not active_prices:
             # Fallback 1: Try Case-Insensitive partial match logic is handled inside helper? 
             # For now, if exact match fails, try default group/level
             print(f"⚠️ Warning: No salary table found for {request.company_slug}/{user_group}/{user_level}. Using defaults.")
             active_prices = {
                 "BASE_ANNUAL": 15876.00, # SMI approx fallback
                 "HORA_EXTRA": 12.0,
                 "HORA_PERENTORIA": 14.0
             }

        # 2. Base Salary Calculation
        # Priority: Request > DB Table > Hardcoded Fallback
        annual_table_salary = request.gross_annual_salary if request.gross_annual_salary > 0 else 0
        
        if annual_table_salary <= 0:
            annual_table_salary = active_prices.get("SALARIO_BASE", active_prices.get("BASE_ANNUAL", 0))
            
        if annual_table_salary <= 0:
             print(f"⚠️ Warning: No salary entry for {request.company_slug}. Using absolute fallback.")
             annual_table_salary = 18450.87 # SMI approx fallback 2024/25

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
        # MAPPING FIX: Sector Companies use 'convenio-sector' definitions
        target_slug_for_definitions = request.company_slug
        if request.company_slug in ["jet2", "norwegian", "south"]:
            target_slug_for_definitions = "convenio-sector"

        # Fetch definitions from DB for this company
        db_concepts = self.db.query(SalaryConceptDefinition).filter(
            SalaryConceptDefinition.company_slug == target_slug_for_definitions,
            SalaryConceptDefinition.is_active == True
        ).all()
        
        start_concept_map = {c.code: c for c in db_concepts}
        
        # Process Dynamic Variables from Request
        if request.dynamic_variables:
            for code, input_val in request.dynamic_variables.items():
                if input_val > 0 and code in start_concept_map:
                    definition = start_concept_map[code]
                    
                    # Determine Unit Price
                    # Default to DB metadata definition
                    unit_price = definition.default_price or 0.0 
                    
                    # Priority 1: Salary Table (Specific for Group/Level)
                    # If this concept matches a column in our extracted tables (e.g. HORA_EXTRA), use legitimate price
                    if code in active_prices:
                        unit_price = active_prices[code]
                    
                    definitions_with_proportionality = ["checkbox", "select"] # Types that imply a fixed monthly status, not a quantity count
                    
                    # Logic: If it's a fixed status (Checkbox/Select), the price is usually monthly full-time -> Apply Prorata
                    # Exception: PLUS_FTP might be specific, but standard pluses (Turnicidad, Jefatura) are proportional.
                    # We assume Checkbox = Proportional.
                    
                    final_unit_price = unit_price
                    if definition.input_type in definitions_with_proportionality:
                        final_unit_price = unit_price * prorata_factor

                    # Calculate Amount based on Input Type
                    if definition.input_type == "currency" or definition.input_type == "manual":
                        # Input IS the monetary amount (e.g. Garantia Personal = 200€) -> User already calculated it or it's fixed
                        # If manually entered, we trust the user.
                        amount = input_val
                    else:
                        # Input is a quantity (Hours, Days) OR a Flag (1.0)
                        amount = input_val * final_unit_price

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
        
        # Max/Min Bases would go here (Topes de Cotización 2025: ~4720.50€ max)
        # Simplified for MVP
        
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

    def _get_salary_prices_from_db(self, company_slug: str, group: str, level: str) -> dict:
        """
        Fetches salary concepts from the database and returns a flattened dictionary
        like {"BASE_ANNUAL": 20000, "HORA_EXTRA": 15.5}
        """
        rows = self.db.query(SalaryTable).filter(
            SalaryTable.company_id == company_slug,
            SalaryTable.group == group,
            SalaryTable.level == level
        ).order_by(SalaryTable.year.desc()).all()
        
        if not rows:
             print(f"🔍 [DB] No exact level match for {company_slug}/{group}/{level}.")
             
             # Fallback Strategy 1: Try adding/removing " - " prefix (Common in EasyJet)
             # If user sends "Nivel 1" but DB has "Agente de Rampa - Nivel 1"
             if " - " not in level:
                 # Try wildcards? No, distinct search.
                 # Partial match fallback
                 rows = self.db.query(SalaryTable).filter(
                     SalaryTable.company_id == company_slug,
                     SalaryTable.group == group,
                     SalaryTable.level.contains(level) # Try to match "Nivel 1" inside "Agente... - Nivel 1"
                 ).all()
                 if rows:
                     print(f"✅ Found partial match for {level}: {[r.level for r in rows][0]}")

             if not rows:
                 print("⚠️ Fallback to Nivel 3 default.")
                 rows = self.db.query(SalaryTable).filter(
                     SalaryTable.company_id == company_slug,
                     SalaryTable.group == group,
                     SalaryTable.level.like("%Nivel 3%") # Relaxed fallback
                 ).all()
             
        prices = {}
        for row in rows:
            # Safeguard: Ensure amount is a float, defaulting to 0.0 if None
            prices[row.concept] = row.amount if row.amount is not None else 0.0
            
        return prices

    def get_formatted_salary_table(self, company_slug: str, group: str, level: str) -> str:
        """
        Returns a Markdown formatted string with the exact salary table data found in DB.
        Used for RAG context injection.
        """
        prices = self._get_salary_prices_from_db(company_slug, group, level)
        
        if not prices:
            return f"❌ No he encontrado datos salariales estructurados para {company_slug} / {group} / {level}."
            
        md = f"""
### 📊 DATOS OFICIALES DE TABLA SALARIAL (Base de Datos)
**Perfil**: {company_slug.upper()} | {group} | {level}
**Año**: 2025

| Concepto | Valor (€) |
| :--- | :--- |
"""
        # Sort keys for consistent output
        for concept, amount in sorted(prices.items()):
            md += f"| {concept} | {amount:,.2f} € |\n"
            
        md += "\n*Estos datos provienen directamente de la calculadora y TIENEN PRIORIDAD sobre cualquier documento general.*"
        return md
