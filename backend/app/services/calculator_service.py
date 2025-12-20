import os
import json
from sqlalchemy.orm import Session
from app.db.models import SalaryTable, SalaryConceptDefinition
from app.schemas.salary import CalculationRequest, SalaryResponse, SalaryConcept
from app.constants import SECTOR_COMPANIES

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
            annual_table_salary = active_prices.get("SALARIO_BASE_ANUAL", active_prices.get("SALARIO_BASE", active_prices.get("BASE_ANNUAL", 0)))
            
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
        
        # --- EASYJET AUTOMATIC CONCEPTS ---
        # For EasyJet, automatically assign Plus Función, Plus Progresión, and Ad Personam
        easyjet_auto_amount = 0.0
        if request.company_slug == "easyjet":
            # Load EasyJet structure to get category-specific data
            easyjet_json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'structure_templates', 'easyjet.json')
            
            try:
                with open(easyjet_json_path, 'r', encoding='utf-8') as f:
                    easyjet_data = json.load(f)
                
                # IMPORTANT: EasyJet has inverted structure
                # user_level = Category name (e.g., "Jefe de Área Tipo A")
                # user_group = Level name (e.g., "Nivel 3")
                
                category_data = None
                level_data = None
                
                # Search for category by name
                for group in easyjet_data['structure']['groups']:
                    for category in group['categories']:
                        if category['name'] == request.user_level:
                            category_data = category
                            # Find specific level within category
                            for level in category.get('levels', []):
                                if level['level'] == request.user_group:
                                    level_data = level
                                    break
                            break
                    if category_data:
                        break
                
                if category_data:
                    print(f"   🔍 Found EasyJet category: {category_data['name']}")
                    if level_data:
                        print(f"   🔍 Found level: {level_data['level']}")
                    
                    # 1. Plus Función (only for Jefes de Área)
                    if 'plus_funcion_fixed' in category_data and category_data['plus_funcion_fixed'] > 0:
                        # Plus Función is annual (×12), convert to monthly
                        plus_funcion_annual = category_data['plus_funcion_fixed']
                        plus_funcion_monthly = plus_funcion_annual / 12.0
                        # NOT proportional to jornada
                        concepts.append(SalaryConcept(
                            name="Plus Función (Categoría)",
                            amount=plus_funcion_monthly,
                            type="devengo"
                        ))
                        easyjet_auto_amount += plus_funcion_monthly
                        print(f"   ✅ Auto-assigned Plus Función: {plus_funcion_monthly:.2f}€")
                    
                    # 2. Plus Progresión (by level)
                    if level_data and 'progression_plus' in level_data and level_data['progression_plus'] > 0:
                        # Progression is annual (×14), convert to monthly and apply prorata
                        progression_annual = level_data['progression_plus']
                        progression_monthly = (progression_annual / 14.0) * prorata_factor
                        concepts.append(SalaryConcept(
                            name=f"Plus Progresión ({level_data['level']})",
                            amount=progression_monthly,
                            type="devengo"
                        ))
                        easyjet_auto_amount += progression_monthly
                        print(f"   ✅ Auto-assigned Plus Progresión: {progression_monthly:.2f}€")
                else:
                    print(f"   ⚠️ Warning: Could not find EasyJet category '{request.user_level}'")
                        
            except Exception as e:
                print(f"   ⚠️ Warning: Could not load EasyJet automatic concepts: {e}")
                import traceback
                traceback.print_exc()
        
        # Calculate total from auto-assigned concepts (EasyJet)
        auto_assigned_total = sum(c.amount for c in concepts if c.type == "devengo")
        
        total_variable = 0
        
        # --- DYNAMIC CONCEPT LOGIC ---
        # MAPPING FIX: Sector Companies use 'convenio-sector' definitions
        target_slug_for_definitions = request.company_slug
        if request.company_slug in SECTOR_COMPANIES:
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
                    
                    # Priority 1: level_values (JSON field in SalaryConceptDefinition)
                    # For concepts like HORA_EXTRA, HORA_PERENTORIA that have different prices per level
                    if definition.level_values and isinstance(definition.level_values, dict):
                        # EasyJet has inverted structure: user_level=category, user_group=level
                        if request.company_slug == "easyjet":
                            lookup_category = user_level  # user_level contains category
                            lookup_level = user_group      # user_group contains level
                        else:
                            lookup_category = user_group
                            lookup_level = user_level
                        
                        if lookup_category in definition.level_values:
                            group_levels = definition.level_values[lookup_category]
                            if isinstance(group_levels, dict) and lookup_level in group_levels:
                                unit_price = group_levels[lookup_level]
                                print(f"   💰 Using level-specific price for {code}: {unit_price}€ ({lookup_category}/{lookup_level})")
                    
                    # Priority 2: Salary Table (Specific for Group/Level)
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
        # Totales
        gross_monthly = base_salary_for_gross + total_variable + easyjet_auto_amount
        
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
        # MAPPING FIX: Sector Companies use 'convenio-sector' tables
        target_slug = company_slug
        if company_slug in SECTOR_COMPANIES:
            target_slug = "convenio-sector"
        
        # EASYJET SPECIFIC LOOKUP
        # EasyJet has inverted structure: user_level=category, user_group=level
        # We need to find the correct group and construct the full level name
        if company_slug == "easyjet":
            # Load EasyJet structure to find the group for this category
            easyjet_json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'structure_templates', 'easyjet.json')
            try:
                with open(easyjet_json_path, 'r', encoding='utf-8') as f:
                    easyjet_data = json.load(f)
                
                # Find which group this category belongs to
                category_name = level  # user_level contains category name
                level_name = group    # user_group contains level name
                
                for grp in easyjet_data['structure']['groups']:
                    for cat in grp['categories']:
                        if cat['name'] == category_name:
                            # Found the category, now construct the full level name
                            actual_group = grp['name']
                            actual_level = f"{category_name} - {level_name}"
                            
                            print(f"   🔍 EasyJet lookup: group='{actual_group}', level='{actual_level}'")
                            
                            # Query with correct group and level
                            rows = self.db.query(SalaryTable).filter(
                                SalaryTable.company_id == target_slug,
                                SalaryTable.group == actual_group,
                                SalaryTable.level == actual_level
                            ).order_by(SalaryTable.year.desc()).all()
                            
                            if rows:
                                prices = {}
                                for row in rows:
                                    prices[row.concept] = row.amount if row.amount is not None else 0.0
                                print(f"   ✅ Found {len(prices)} concepts for EasyJet")
                                return prices
                            break
            except Exception as e:
                print(f"   ⚠️ EasyJet lookup failed: {e}")
        
        # NORMAL LOOKUP (for other companies)
        rows = self.db.query(SalaryTable).filter(
            SalaryTable.company_id == target_slug,
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

    def get_group_salary_table_markdown(self, company_slug: str, group: str) -> str:
        """
        Returns a Markdown table containing salary data for ALL levels in the specified group.
        This enables the RAG to perform comparisons between levels (e.g. "Level 1 vs Level 3").
        """
        # MAPPING FIX: Sector Companies use 'convenio-sector'
        target_slug = company_slug
        if company_slug in SECTOR_COMPANIES:
            target_slug = "convenio-sector"
            
        print(f"📊 Fetching GROUP table for {target_slug} / {group}")

        # Fetch all levels for this group
        # EasyJet Exception: Group is part of Level Name in DB? 
        # No, in DB EasyJet has: Group="Servicios Auxiliares", Level="Agente de Rampa - Nivel 3"
        # So filtering by Group should work fine.
        
        rows = self.db.query(SalaryTable).filter(
            SalaryTable.company_id == target_slug,
            SalaryTable.group == group
        ).order_by(SalaryTable.level, SalaryTable.year.desc()).all()
        
        if not rows:
            return ""

        # Organize by Level -> Concept -> Amount
        data = {}
        concepts = set()
        
        for row in rows:
            lvl = row.level
            if lvl not in data:
                data[lvl] = {}
            # Keep only the latest year if duplicates exist (handled by order_by, but dict overwrites sequentially if multiple years, we want latest first... wait, list is ordered by year desc, so first one is latest)
            # Actually if we iterate, we might overwrite with older years if we don't check.
            # Let's simple check if concept exists.
            if row.concept not in data[lvl]:
                data[lvl][row.concept] = row.amount
                concepts.add(row.concept)

        if not data:
            return ""
            
        # Prioritize Key Concepts for readability
        priority_concepts = ["SALARIO_BASE", "SALARIO_BASE_ANUAL", "SALARIO_BASE_MENSUAL", "PLUS_NOCTURNIDAD", "HORA_EXTRA", "HORA_PERENTORIA"]
        sorted_concepts = sorted(list(concepts))
        
        # Move priority to front
        final_columns = []
        for p in priority_concepts:
            if p in sorted_concepts:
                final_columns.append(p)
                sorted_concepts.remove(p)
        
        # Add ALL remaining concepts (User requested full details)
        final_columns.extend(sorted_concepts)
        
        # Build Markdown
        md = f"""
### 📊 TABLA SALARIAL COMPLETA: {group.upper()} (2025)
Esta tabla contiene los valores oficiales para TODOS los niveles del grupo {group}. Úsala para comparaciones.

| Nivel | {' | '.join(final_columns)} |
| :--- | {' | '.join([':---'] * len(final_columns))} |
"""
        # Sort levels naturally if possible
        def logical_sort(lvl):
            # Try to extract number for sorting "Nivel 4" vs "Nivel 10"
            tokens = lvl.split()
            for t in tokens:
                if t.isdigit():
                    return int(t)
            return lvl

        try:
             sorted_levels = sorted(data.keys(), key=logical_sort)
        except:
             sorted_levels = sorted(data.keys())

        for level_name in sorted_levels:
            row_str = f"| **{level_name}**"
            for col in final_columns:
                val = data[level_name].get(col, 0.0)
                if val == 0:
                     row_str += " | -"
                else:
                     row_str += f" | {val:,.2f}€"
            row_str += " |"
            md += row_str + "\n"

        return md

