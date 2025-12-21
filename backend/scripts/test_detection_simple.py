"""
Test Simplificado - Sin API Key
Prueba solo la detección de cálculo (no requiere LLM)
"""
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

print("="*70)
print("TEST SIMPLIFICADO - DETECCIÓN DE CÁLCULO")
print("="*70)

# Test sin inicializar rag_engine completo
def test_calculation_detection_logic():
    """Test de la lógica de detección"""
    
    def _is_calculation_query(query: str) -> bool:
        """Copia de la lógica de detección"""
        q = query.lower()
        
        # 1. Keywords de operación
        op_keywords = [
            'diferencia', 'cuanto más', 'cuanto menos', 'cuánto más', 'cuánto menos',
            'incremento', 'aumento', 'reducción', 'comparar', 'vs', 'versus',
            'calcular', 'calcula'
        ]
        
        # 2. Keywords de contexto
        context_keywords = [
            'nivel', 'grupo', 'salario', 'sueldo', 'cobrar', 'paga', 'plus', 
            'retribución', 'bruto', 'neto', 'anual', 'mensual'
        ]
        
        # Lógica
        has_op = any(kw in q for kw in op_keywords)
        has_context = any(kw in q for kw in context_keywords)
        has_numbers = any(char.isdigit() for char in q)
        
        return has_op and (has_context or has_numbers)
    
    test_cases = [
        # Debería detectar (True)
        ("diferencia salarial nivel 3 y 4", True, "operación + contexto + números"),
        ("cuanto más cobra nivel 5", True, "operación + contexto + número"),
        ("incremento entre grupo A y B", True, "operación + contexto"),
        ("calcular diferencia nivel 3 nivel 4", True, "operación + contexto + números"),
        ("comparar salario nivel 2 vs nivel 3", True, "operación + contexto + números"),
        ("aumento de sueldo", True, "operación + contexto"),
        
        # NO debería detectar (False)
        ("diferencia entre vacaciones y permisos", False, "operación sin contexto salarial"),
        ("cuales son las vacaciones", False, "sin operación"),
        ("salario base", False, "solo contexto, sin operación"),
        ("nivel 3", False, "solo número, sin operación"),
        ("incremento de vacaciones", False, "operación sin contexto salarial"),
    ]
    
    print("\n📊 Test Cases:")
    print("-"*70)
    
    passed = 0
    for query, expected, reason in test_cases:
        result = _is_calculation_query(query)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{query}'")
        print(f"   → Detectado: {result} | Esperado: {expected}")
        print(f"   → Razón: {reason}")
        print()
        if result == expected:
            passed += 1
    
    print("="*70)
    print(f"RESULTADO: {passed}/{len(test_cases)} tests pasados")
    print("="*70)
    
    if passed == len(test_cases):
        print("\n🎉 TODOS LOS TESTS PASARON")
        return 0
    else:
        print(f"\n❌ {len(test_cases) - passed} tests fallaron")
        return 1


if __name__ == "__main__":
    exit(test_calculation_detection_logic())
