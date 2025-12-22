"""
Query Expansion Service - Capa 1 del Sistema RAG Híbrido (Elite Version)

Utiliza Gemini Flash para normalizar y expandir consultas de usuario
a términos jurídicos antes de la búsqueda vectorial.

Validado por 8 opiniones expertas - Nivel producción enterprise.
"""
import os
import json
import re
import logging
import google.generativeai as genai
from typing import Dict, Any, List, Set

logger = logging.getLogger(__name__)

class QueryExpander:
    """
    Capa 1 del RAG: Normalización semántica de la consulta del usuario.
    Usa Gemini Flash para transformar lenguaje natural en intents y keywords jurídicas.
    """

    # MEJORA ELITE 1: Validación estricta de Intents permitidos
    ALLOWED_INTENTS: Set[str] = {"LEAVE", "SALARY", "DISMISSAL", "GENERAL"}

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY no encontrada. El QueryExpander funcionará en modo fallback.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            # Usar gemini-2.0-flash-exp (más reciente y potente)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def expand(self, query: str) -> Dict[str, Any]:
        """
        Analiza la query del usuario y devuelve una estructura JSON normalizada.
        
        Args:
            query (str): "Mi tío está malo"
            
        Returns:
            Dict: {
                "intent": "LEAVE",
                "keywords_busqueda": ["permiso retribuido", "hospitalización", ...],
                "entidades_detectadas": ["tío"],
                "requiere_tablas": True,
                "meta": {"source": "flash", "status": "ok"}
            }
        """
        # Estructura de fallback por defecto
        fallback_result = {
            "intent": "GENERAL",
            "keywords_busqueda": [self._clean_keyword(query)], 
            "entidades_detectadas": [],
            "requiere_tablas": False,
            "meta": {"source": "fallback", "reason": "init_error"}
        }

        if not self.model:
            return fallback_result

        # Prompt optimizado para clasificación jurídica
        prompt = f"""
        Actúa como un middleware de búsqueda jurídica para un sistema de Handling Aeroportuario (España).
        Tu objetivo es traducir la consulta del usuario a términos de búsqueda precisos para un buscador vectorial.

        Consulta Usuario: "{query}"

        Instrucciones:
        1. Identifica el Intent Principal (SOLO UNO): 
           - LEAVE (Vacaciones, Permisos, Bajas, Días libres)
           - SALARY (Nómina, Tablas, Pluses, Horas extra, Diferencias salariales)
           - DISMISSAL (Despido, Finiquito, Sanciones)
           - GENERAL (Otros temas)
        2. Genera 'keywords_busqueda': Lista de 3-5 términos jurídicos/técnicos sinónimos.
           - Ej: "tío malo" -> ["permiso retribuido", "hospitalización", "enfermedad grave", "parientes"]
           - Ej: "cuanto cobro nivel 3" -> ["tabla salarial", "retribución anual", "grupo profesional"]
        3. Detecta 'requiere_tablas': true si la pregunta implica valores numéricos, salarios o grados de parentesco.

        Devuelve SOLO un JSON válido con este formato:
        {{
            "intent": "STRING",
            "keywords_busqueda": ["STRING", ...],
            "entidades_detectadas": ["STRING", ...],
            "requiere_tablas": boolean
        }}
        """

        try:
            # MEJORA ELITE 2: SDK oficial + response_mime_type (fuerza JSON limpio)
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.0,  # Máximo determinismo
                    "response_mime_type": "application/json"
                }
            )

            raw_text = response.text.strip()
            
            # Limpieza defensiva: Eliminar bloques markdown si se escapan
            cleaned_text = re.sub(r'```json\n?|\n?```', '', raw_text)
            
            data = json.loads(cleaned_text)
            
            # --- APLICANDO MEJORAS DE NIVEL ÉLITE ---

            # MEJORA ELITE 3: Validación de Intent (Sanitización)
            intent = data.get("intent", "GENERAL").upper()
            if intent not in self.ALLOWED_INTENTS:
                logger.warning(f"Intent desconocido detectado: '{intent}'. Forzando GENERAL.")
                intent = "GENERAL"

            # MEJORA ELITE 4: Normalización de Keywords (Limpieza)
            raw_keywords = data.get("keywords_busqueda", [])
            # Si Flash falla y devuelve lista vacía, usamos la query original
            if not raw_keywords:
                raw_keywords = [query]
                
            clean_keywords = [
                self._clean_keyword(k) 
                for k in raw_keywords 
                if k and len(k) < 60  # Evitar alucinaciones de frases muy largas
            ]

            requiere_tablas = data.get("requiere_tablas", False)

            # MEJORA ELITE 5: Logging Estructurado (Métrica de Calidad)
            logger.info(
                f"QueryExpanded | Query: '{query[:30]}...' | Intent: {intent} | "
                f"Tablas: {requiere_tablas} | KW: {len(clean_keywords)}"
            )

            return {
                "intent": intent,
                "keywords_busqueda": clean_keywords,
                "entidades_detectadas": data.get("entidades_detectadas", []),
                "requiere_tablas": requiere_tablas,
                "meta": {"source": "flash", "status": "ok"}
            }

        except Exception as e:
            logger.error(f"Error crítico en QueryExpander: {str(e)}", exc_info=True)
            fallback_result["meta"]["reason"] = str(e)
            return fallback_result

    def _clean_keyword(self, keyword: str) -> str:
        """Helper para limpiar keywords (minúsculas, espacios extra, puntuación)."""
        # Eliminar caracteres no alfanuméricos del inicio/final (puntuación)
        clean = keyword.strip()
        # Eliminar interrogaciones y puntos finales que rompen búsqueda exacta
        clean = clean.rstrip("?.!,;:")
        return clean.lower()

    def get_expanded_query_text(self, expansion: Dict) -> str:
        """
        Convierte la expansión a texto para búsqueda vectorial.
        
        Args:
            expansion: Resultado de expand()
        
        Returns:
            String optimizado para búsqueda
        """
        return " ".join(expansion["keywords_busqueda"])

# --- BLOQUE DE PRUEBA (Ejecutar directamente este archivo) ---
if __name__ == "__main__":
    # Configura Logging para ver los mensajes en consola
    logging.basicConfig(level=logging.INFO)
    
    # os.environ["GOOGLE_API_KEY"] = "TU_API_KEY"
    
    expander = QueryExpander()
    
    test_queries = [
        "Mi tío está malo y lo van a ingresar",  # Debería ser LEAVE + Tablas
        "Hola guapo",                            # Debería ser GENERAL (Chit-chat)
        "Diferencia sueldo nivel 3 y 4",         # Debería ser SALARY + Tablas
        "cuánto cobra un agente de rampa nivel 3",
        "me han sancionado injustamente",
        "quiero reclamar horas extras"
    ]
    
    print("\n" + "=" * 70)
    print("PRUEBA DE QUERY EXPANSION (Elite Version)")
    print("=" * 70)
    
    for q in test_queries:
        print(f"\n📝 Query original: '{q}'")
        result = expander.expand(q)
        
        print(f"   Intent: {result['intent']}")
        print(f"   Keywords: {result['keywords_busqueda']}")
        print(f"   Entidades: {result['entidades_detectadas']}")
        print(f"   Requiere tablas: {result['requiere_tablas']}")
        print(f"   Meta: {result['meta']}")
        print(f"   → Búsqueda: '{expander.get_expanded_query_text(result)}'")
        print("-" * 70)

