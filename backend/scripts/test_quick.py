"""
Test Simple - Fase 2: Validación Rápida
"""
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

print("=" * 70)
print("TEST RAPIDO - FASE 2")
print("=" * 70)

# Test 1: Import
print("\n[Test 1] Importando módulos...")
try:
    from app.services.hybrid_calculator import (
        HybridSalaryCalculator,
        SalaryData,
        CalculationResult
    )
    print("OK - Imports correctos")
except Exception as e:
    print(f"FAIL - Error: {e}")
    exit(1)

# Test 2: Crear SalaryData
print("\n[Test 2] Creando SalaryData...")
try:
    data = SalaryData(
        level_origin=25000.0,
        level_destination=28000.0,
        field_name="salario base",
        company="azul-handling",
        year=2025
    )
    print(f"OK - Origin: {data.level_origin}, Destination: {data.level_destination}")
except Exception as e:
    print(f"FAIL - Error: {e}")
    exit(1)

# Test 3: Crear CalculationResult
print("\n[Test 3] Creando CalculationResult...")
try:
    result = CalculationResult(
        difference=3000.0,
        percentage=12.0,
        level_origin_value=25000.0,
        level_destination_value=28000.0,
        field_name="salario base",
        calculation_type="difference"
    )
    print(f"OK - Diferencia: {result.difference}, Porcentaje: {result.percentage}%")
except Exception as e:
    print(f"FAIL - Error: {e}")
    exit(1)

# Test 4: Verificar metadata en BD
print("\n[Test 4] Verificando metadata en BD...")
try:
    from app.db.database import SessionLocal
    from app.db.models import DocumentChunk
    
    db = SessionLocal()
    count = db.query(DocumentChunk).filter(
        DocumentChunk.chunk_metadata['type'].astext == 'table'
    ).count()
    print(f"OK - Tablas en BD: {count}")
    db.close()
except Exception as e:
    print(f"FAIL - Error: {e}")
    exit(1)

# Test 5: Verificar calculadora en rag_engine
print("\n[Test 5] Verificando calculadora en rag_engine...")
try:
    from app.services.rag_engine import rag_engine
    
    if hasattr(rag_engine, 'hybrid_calculator'):
        if rag_engine.hybrid_calculator:
            print("OK - Calculadora inicializada")
        else:
            print("WARNING - Calculadora es None (GOOGLE_API_KEY no configurada?)")
    else:
        print("FAIL - rag_engine no tiene hybrid_calculator")
        exit(1)
except Exception as e:
    print(f"FAIL - Error: {e}")
    exit(1)

print("\n" + "=" * 70)
print("TODOS LOS TESTS BASICOS PASARON")
print("=" * 70)
