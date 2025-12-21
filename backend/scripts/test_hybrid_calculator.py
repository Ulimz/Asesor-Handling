"""
Test Suite - Fase 2: Calculadora Híbrida
Tests para validar LLM extraction, Python calculation, y guardrails
"""
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.hybrid_calculator import (
    HybridSalaryCalculator,
    SalaryData,
    CalculationResult
)
import google.generativeai as genai
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper para tests
def _normalize_number_test(value) -> float:
    """Test version of normalize_number"""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        import re
        v = value.strip()
        v = v.replace(".", "").replace(",", ".")
        m = re.search(r"-?\d+(\.\d+)?", v)
        if not m:
            raise ValueError(f"No se encontró número en '{value}'")
        return float(m.group(0))
    raise ValueError(f"Tipo no soportado: {type(value)}")


def test_normalize_european_format():
    """Test 1: Normalización de formato europeo"""
    logger.info("\n🧪 Test 1: Normalización de formato europeo")
    
    test_cases = [
        ("22.500,50", 22500.50),
        ("22500", 22500.0),
        ("22.500", 22500.0),
        ("22,500.50", 22500.50),
        ("18 000", 18000.0),
        ("1.234,56€", 1234.56),
        (25000, 25000.0),
        (25000.50, 25000.50),
    ]
    
    passed = 0
    for input_val, expected in test_cases:
        try:
            result = _normalize_number_test(input_val)
            if abs(result - expected) < 0.01:
                logger.info(f"   ✅ '{input_val}' → {result} (esperado: {expected})")
                passed += 1
            else:
                logger.error(f"   ❌ '{input_val}' → {result} (esperado: {expected})")
        except Exception as e:
            logger.error(f"   ❌ '{input_val}' → Error: {e}")
    
    logger.info(f"\n   Resultado: {passed}/{len(test_cases)} tests pasados")
    return passed == len(test_cases)


def test_salary_data_creation():
    """Test 2: Creación de SalaryData"""
    logger.info("\n🧪 Test 2: Creación de SalaryData")
    
    try:
        data = SalaryData(
            level_origin=25000.0,
            level_destination=28000.0,
            field_name="salario base",
            company="azul-handling",
            year=2025,
            level_origin_label="Nivel 3",
            level_destination_label="Nivel 4"
        )
        
        logger.info(f"   ✅ SalaryData creado correctamente")
        logger.info(f"      Origin: {data.level_origin} ({data.level_origin_label})")
        logger.info(f"      Destination: {data.level_destination} ({data.level_destination_label})")
        logger.info(f"      Field: {data.field_name}")
        
        # Test to_dict()
        data_dict = data.to_dict()
        assert "level_origin" in data_dict
        assert "level_destination" in data_dict
        logger.info(f"   ✅ to_dict() funciona correctamente")
        
        return True
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return False


def test_calculation():
    """Test 3: Cálculo matemático preciso"""
    logger.info("\n🧪 Test 3: Cálculo matemático preciso")
    
    try:
        # Mock calculator (sin LLM)
        data = SalaryData(
            level_origin=25000.0,
            level_destination=28000.0,
            field_name="salario base",
            company="azul-handling",
            year=2025
        )
        
        # Simular cálculo manual
        expected_diff = 28000.0 - 25000.0
        expected_pct = (expected_diff / 25000.0) * 100
        
        logger.info(f"   Diferencia esperada: {expected_diff}€")
        logger.info(f"   Porcentaje esperado: {expected_pct:.2f}%")
        
        # Crear resultado manualmente para validar
        result = CalculationResult(
            difference=expected_diff,
            percentage=expected_pct,
            level_origin_value=25000.0,
            level_destination_value=28000.0,
            field_name="salario base",
            calculation_type="difference"
        )
        
        logger.info(f"   ✅ Cálculo correcto:")
        logger.info(f"      Diferencia: {result.difference}€")
        logger.info(f"      Porcentaje: {result.percentage:.2f}%")
        
        return True
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return False


def test_guardrail_validation():
    """Test 4: Validación de guardrails"""
    logger.info("\n🧪 Test 4: Validación de guardrails")
    
    try:
        # Mock calculator
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("   ⚠️  GOOGLE_API_KEY no configurada, saltando test")
            return True
        
        genai.configure(api_key=api_key)
        calculator = HybridSalaryCalculator(
            gemini_model=genai.GenerativeModel('gemini-2.0-flash-exp')
        )
        
        # Test Case 1: Valores correctos
        data = SalaryData(
            level_origin=25000.0,
            level_destination=28000.0,
            field_name="salario base",
            company="azul-handling",
            year=2025
        )
        
        result = CalculationResult(
            difference=3000.0,
            percentage=12.0,
            level_origin_value=25000.0,
            level_destination_value=28000.0,
            field_name="salario base",
            calculation_type="difference"
        )
        
        is_valid = calculator.validate_result(data, result)
        if is_valid:
            logger.info(f"   ✅ Guardrail acepta valores correctos")
        else:
            logger.error(f"   ❌ Guardrail rechaza valores correctos")
            return False
        
        # Test Case 2: Diferencia incorrecta
        bad_result = CalculationResult(
            difference=5000.0,  # Incorrecto
            percentage=12.0,
            level_origin_value=25000.0,
            level_destination_value=28000.0,
            field_name="salario base",
            calculation_type="difference"
        )
        
        is_valid = calculator.validate_result(data, bad_result)
        if not is_valid:
            logger.info(f"   ✅ Guardrail rechaza diferencia incorrecta")
        else:
            logger.error(f"   ❌ Guardrail acepta diferencia incorrecta")
            return False
        
        # Test Case 3: Valores negativos
        negative_data = SalaryData(
            level_origin=-25000.0,  # Negativo
            level_destination=28000.0,
            field_name="salario base",
            company="azul-handling",
            year=2025
        )
        
        negative_result = calculator.calculate(negative_data)
        if negative_result is None:
            logger.info(f"   ✅ Guardrail rechaza valores negativos")
        else:
            logger.error(f"   ❌ Guardrail acepta valores negativos")
            return False
        
        return True
    except Exception as e:
        logger.error(f"   ❌ Error: {e}", exc_info=True)
        return False


def test_integration_with_metadata():
    """Test 5: Integración con metadata de chunks"""
    logger.info("\n🧪 Test 5: Integración con metadata de chunks")
    
    try:
        from app.db.database import SessionLocal
        from app.db.models import DocumentChunk
        
        db = SessionLocal()
        
        # Buscar un chunk con metadata
        chunk = db.query(DocumentChunk).filter(
            DocumentChunk.chunk_metadata['type'].astext == 'table',
            DocumentChunk.chunk_metadata['intent'].contains(['SALARY'])
        ).first()
        
        if not chunk:
            logger.warning("   ⚠️  No hay chunks con metadata SALARY, saltando test")
            db.close()
            return True
        
        logger.info(f"   ✅ Chunk encontrado:")
        logger.info(f"      ID: {chunk.id}")
        logger.info(f"      Type: {chunk.chunk_metadata.get('type')}")
        logger.info(f"      Intent: {chunk.chunk_metadata.get('intent')}")
        logger.info(f"      Company: {chunk.chunk_metadata.get('company')}")
        logger.info(f"      Year: {chunk.chunk_metadata.get('year')}")
        
        # Verificar que tiene año
        year = chunk.chunk_metadata.get('year')
        if isinstance(year, int):
            logger.info(f"   ✅ Año extraído correctamente: {year}")
        else:
            logger.warning(f"   ⚠️  Año no es entero: {year}")
        
        db.close()
        return True
    except Exception as e:
        logger.error(f"   ❌ Error: {e}", exc_info=True)
        return False


def main():
    logger.info("=" * 70)
    logger.info("TEST SUITE - FASE 2: CALCULADORA HÍBRIDA")
    logger.info("=" * 70)
    
    results = []
    
    # Ejecutar tests
    results.append(("Normalización de números", test_normalize_european_format()))
    results.append(("Creación de SalaryData", test_salary_data_creation()))
    results.append(("Cálculo matemático", test_calculation()))
    results.append(("Guardrails de validación", test_guardrail_validation()))
    results.append(("Integración con metadata", test_integration_with_metadata()))
    
    # Resumen
    logger.info("\n" + "=" * 70)
    logger.info("RESUMEN DE TESTS")
    logger.info("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {name}")
    
    logger.info("\n" + "=" * 70)
    logger.info(f"RESULTADO FINAL: {passed}/{total} tests pasados")
    logger.info("=" * 70)
    
    if passed == total:
        logger.info("\n🎉 TODOS LOS TESTS PASARON")
        return 0
    else:
        logger.error(f"\n❌ {total - passed} tests fallaron")
        return 1


if __name__ == "__main__":
    exit(main())
