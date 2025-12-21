"""
Test de Integración - Calculadora Híbrida en search()
Prueba el flujo completo: detección → Legal Anchors → cálculo → respuesta
"""
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.db.database import SessionLocal
from app.services.rag_engine import rag_engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_calculation_detection():
    """Test 1: Detección de queries de cálculo"""
    logger.info("\n" + "="*70)
    logger.info("TEST 1: Detección de Queries de Cálculo")
    logger.info("="*70)
    
    test_cases = [
        # Debería detectar (True)
        ("diferencia salarial nivel 3 y 4", True),
        ("cuanto más cobra nivel 5", True),
        ("incremento entre grupo A y B", True),
        ("calcular diferencia nivel 3 nivel 4", True),
        ("comparar salario nivel 2 vs nivel 3", True),
        
        # NO debería detectar (False)
        ("diferencia entre vacaciones y permisos", False),
        ("cuales son las vacaciones", False),
        ("salario base", False),
        ("nivel 3", False),
    ]
    
    passed = 0
    for query, expected in test_cases:
        result = rag_engine._is_calculation_query(query)
        status = "✅" if result == expected else "❌"
        logger.info(f"{status} '{query}' → {result} (esperado: {expected})")
        if result == expected:
            passed += 1
    
    logger.info(f"\nResultado: {passed}/{len(test_cases)} tests pasados")
    return passed == len(test_cases)


def test_full_calculation_flow():
    """Test 2: Flujo completo de cálculo"""
    logger.info("\n" + "="*70)
    logger.info("TEST 2: Flujo Completo de Cálculo")
    logger.info("="*70)
    
    db = SessionLocal()
    
    try:
        # Query de cálculo
        query = "diferencia salarial nivel 3 y 4"
        company_slug = "azul-handling"
        
        logger.info(f"\nQuery: '{query}'")
        logger.info(f"Company: {company_slug}")
        
        # Ejecutar búsqueda
        results = rag_engine.search(
            query=query,
            company_slug=company_slug,
            db=db,
            limit=5
        )
        
        if not results:
            logger.error("❌ No se obtuvieron resultados")
            return False
        
        result = results[0]
        
        # Verificar estructura de respuesta
        logger.info(f"\n📊 Resultado:")
        logger.info(f"   ID: {result.get('id')}")
        logger.info(f"   Article Ref: {result.get('article_ref')}")
        logger.info(f"   Score: {result.get('score')}")
        
        # Verificar si tiene cálculo
        if 'calculation' in result:
            logger.info(f"\n✅ Cálculo detectado:")
            calc = result['calculation']
            logger.info(f"   Diferencia: {calc.get('difference')}€")
            logger.info(f"   Porcentaje: {calc.get('percentage')}%")
            logger.info(f"   Origen: {calc.get('level_origin_value')}€")
            logger.info(f"   Destino: {calc.get('level_destination_value')}€")
            logger.info(f"   Campo: {calc.get('field_name')}")
            
            # Verificar contenido formateado
            content = result.get('content', '')
            logger.info(f"\n📝 Respuesta formateada:")
            logger.info(f"{content[:200]}...")
            
            return True
        else:
            logger.warning("⚠️ No se encontró campo 'calculation' en resultado")
            logger.info(f"   Content: {result.get('content', '')[:200]}...")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return False
    finally:
        db.close()


def test_fallback_to_rag():
    """Test 3: Fallback a RAG estándar"""
    logger.info("\n" + "="*70)
    logger.info("TEST 3: Fallback a RAG Estándar")
    logger.info("="*70)
    
    db = SessionLocal()
    
    try:
        # Query normal (no cálculo)
        query = "vacaciones en azul handling"
        company_slug = "azul-handling"
        
        logger.info(f"\nQuery: '{query}'")
        logger.info(f"Company: {company_slug}")
        
        # Ejecutar búsqueda
        results = rag_engine.search(
            query=query,
            company_slug=company_slug,
            db=db,
            limit=5
        )
        
        if not results:
            logger.warning("⚠️ No se obtuvieron resultados")
            return True  # Es aceptable para queries normales
        
        result = results[0]
        
        # Verificar que NO tiene cálculo
        if 'calculation' not in result or result.get('calculation') is None:
            logger.info("✅ Flujo RAG estándar funcionando correctamente")
            logger.info(f"   Resultados: {len(results)}")
            logger.info(f"   Primer resultado: {result.get('article_ref', 'N/A')}")
            return True
        else:
            logger.error("❌ Query normal detectada como cálculo")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return False
    finally:
        db.close()


def test_no_tables_fallback():
    """Test 4: Fallback cuando no hay tablas"""
    logger.info("\n" + "="*70)
    logger.info("TEST 4: Fallback sin Tablas Disponibles")
    logger.info("="*70)
    
    db = SessionLocal()
    
    try:
        # Query de cálculo pero sin company (menos probable encontrar tablas)
        query = "diferencia nivel 3 y 4"
        
        logger.info(f"\nQuery: '{query}'")
        logger.info(f"Company: None (sin filtro)")
        
        # Ejecutar búsqueda
        results = rag_engine.search(
            query=query,
            company_slug=None,
            db=db,
            limit=5
        )
        
        # Debería retornar algo (fallback a RAG o cálculo si encuentra tablas)
        if results:
            logger.info(f"✅ Sistema respondió con {len(results)} resultados")
            logger.info(f"   Tiene cálculo: {'calculation' in results[0]}")
            return True
        else:
            logger.warning("⚠️ No se obtuvieron resultados")
            return True  # Aceptable
            
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return False
    finally:
        db.close()


def main():
    logger.info("="*70)
    logger.info("TEST SUITE - INTEGRACIÓN CALCULADORA HÍBRIDA")
    logger.info("="*70)
    
    # Verificar que el motor está inicializado
    if not rag_engine.hybrid_calculator:
        logger.error("❌ Hybrid calculator no inicializada")
        logger.error("   Asegúrate de que GOOGLE_API_KEY está configurada")
        return 1
    
    logger.info("✅ Hybrid calculator inicializada")
    
    results = []
    
    # Ejecutar tests
    results.append(("Detección de cálculo", test_calculation_detection()))
    results.append(("Flujo completo de cálculo", test_full_calculation_flow()))
    results.append(("Fallback a RAG estándar", test_fallback_to_rag()))
    results.append(("Fallback sin tablas", test_no_tables_fallback()))
    
    # Resumen
    logger.info("\n" + "="*70)
    logger.info("RESUMEN DE TESTS")
    logger.info("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {name}")
    
    logger.info("\n" + "="*70)
    logger.info(f"RESULTADO FINAL: {passed}/{total} tests pasados")
    logger.info("="*70)
    
    if passed == total:
        logger.info("\n🎉 TODOS LOS TESTS DE INTEGRACIÓN PASARON")
        return 0
    else:
        logger.error(f"\n❌ {total - passed} tests fallaron")
        return 1


if __name__ == "__main__":
    exit(main())
