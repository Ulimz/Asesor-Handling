class LegalEngine:
    @staticmethod
    def calculate_payroll(gross_annual_salary: float, age: int, payments: int):
        # 1. Seguridad Social (6.35% a cargo del trabajador aprox)
        ss_rate = 0.0635
        ss_amount_annual = gross_annual_salary * ss_rate

        # 2. IRPF (Simplificado para MVP)
        # Tramos 2024 aproximados
        base_imponible = gross_annual_salary - ss_amount_annual - 2000 # 2000 gastos deducibles genéricos
        
        if base_imponible < 12450:
            irpf_rate = 0.19
        elif base_imponible < 20200:
            irpf_rate = 0.24
        elif base_imponible < 35200:
            irpf_rate = 0.30
        elif base_imponible < 60000:
            irpf_rate = 0.37
        elif base_imponible < 300000:
            irpf_rate = 0.45
        else:
            irpf_rate = 0.47
            
        # Ajuste progresivo muy simplificado (tipo medio estimado)
        effective_irpf_rate = irpf_rate * 0.7 
        
        irpf_amount_annual = base_imponible * effective_irpf_rate
        annual_net = gross_annual_salary - ss_amount_annual - irpf_amount_annual
        
        return {
            "gross_monthly": round(gross_annual_salary / payments, 2),
            "net_monthly": round(annual_net / payments, 2),
            "irpf_percentage": round(effective_irpf_rate * 100, 2),
            "irpf_amount": round(irpf_amount_annual, 2),
            "social_security_amount": round(ss_amount_annual, 2),
            "annual_net": round(annual_net, 2)
        }

legal_engine = LegalEngine()
