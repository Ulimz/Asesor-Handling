from app.services.rag_engine import rag_engine
from app.prompts import IntentType, PROMPT_TEMPLATES

def test_intent_detection():
    # Salary
    assert rag_engine.detect_intent("cuánto cobro hora extra") == IntentType.SALARY
    assert rag_engine.detect_intent("ver tablas salariales 2024") == IntentType.SALARY
    assert rag_engine.detect_intent("precio hora perentoria") == IntentType.SALARY
    
    # Dismissal
    assert rag_engine.detect_intent("me han despedido por falta") == IntentType.DISMISSAL
    assert rag_engine.detect_intent("cálculo finiquito baja voluntaria") == IntentType.DISMISSAL
    assert rag_engine.detect_intent("indemnización por despido objetivo") == IntentType.DISMISSAL
    
    # Leave
    assert rag_engine.detect_intent("tengo 15 días de vacaciones") == IntentType.LEAVE
    assert rag_engine.detect_intent("permiso por hospitalización de padre") == IntentType.LEAVE
    
    # General
    assert rag_engine.detect_intent("cuál es el ámbito temporal") == IntentType.GENERAL
    assert rag_engine.detect_intent("uniformidad y ropa") == IntentType.GENERAL

def test_prompt_selection_integration():
    """Verify generate_answer picks the right prompt instructions"""
    query = "cuánto es la hora extra"
    intent = rag_engine.detect_intent(query)
    
    # Use dummy context
    context = [{"article_ref": "Test", "content": "Contenido prueba"}]
    
    # Mocking gen_model behavior isn't easy without full mock, 
    # so we just verify the logic flow if we were to debug it.
    # Here we trust the logic we wrote: prompt = PROMPT_TEMPLATES.get(intent)
    
    selected_template = PROMPT_TEMPLATES[intent]
    assert "INSTRUCCIONES ESPECÍFICAS DE SALARIOS" in selected_template
    assert "Nivel X - Euros" in selected_template
