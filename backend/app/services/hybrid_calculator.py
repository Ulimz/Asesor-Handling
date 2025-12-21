"""
Calculadora Híbrida - Fase 2 (Senior-Level)
LLM: Razonamiento y extracción
Python: Cálculo matemático preciso con guardrails
Mejoras: Inferencia determinista, validación estricta, logging QA
"""

import logging
import json
import re
from typing import Optional, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SalaryData:
    """Datos extraídos de la tabla salarial."""
    level_origin: float
    level_destination: float
    field_name: str
    company: str
    year: int
    level_origin_label: str = "nivel origen"
    level_destination_label: str = "nivel destino"
    is_simple_query: bool = False  # True si es "cuánto cobra X"

    def to_dict(self) -> dict:
        return {
            "level_origin": self.level_origin,
            "level_destination": self.level_destination,
            "field_name": self.field_name,
            "company": self.company,
            "year": self.year,
            "level_origin_label": self.level_origin_label,
            "level_destination_label": self.level_destination_label,
            "is_simple_query": self.is_simple_query,
        }


@dataclass
class CalculationResult:
    """Resultado del cálculo con metadata."""
    difference: float
    percentage: float
    level_origin_value: float
    level_destination_value: float
    field_name: str
    calculation_type: str  # "difference", "simple_query"

    def to_dict(self) -> dict:
        return {
            "difference": self.difference,
            "percentage": self.percentage,
            "level_origin_value": self.level_origin_value,
            "level_destination_value": self.level_destination_value,
            "field_name": self.field_name,
            "calculation_type": self.calculation_type,
        }


class HybridSalaryCalculator:
    """Calculadora con guardrail matemático y lógica determinista."""

    def __init__(self, gemini_model):
        """
        Args:
            gemini_model: Instancia de genai.GenerativeModel
        """
        self.model = gemini_model

    def _extract_levels_from_table(self, table_content: str) -> List[int]:
        """
        MEJORA 1: Extrae niveles disponibles en la tabla (Python, no LLM).
        
        Returns:
            Lista de niveles ordenados (ej: [1, 2, 3, 4, 5])
        """
        # Buscar patrones: "Nivel 3", "Grupo 4", "Categoría 5"
        patterns = [
            r'nivel\s+(\d+)',
            r'grupo\s+(\d+)',
            r'categor[ií]a\s+(\d+)',
        ]
        
        levels = set()
        for pattern in patterns:
            matches = re.findall(pattern, table_content.lower())
            levels.update(int(m) for m in matches)
        
        return sorted(list(levels))

    def _infer_comparison_level(
        self,
        mentioned_level: int,
        available_levels: List[int]
    ) -> Optional[int]:
        """
        MEJORA 1: Infiere el nivel de comparación (Python, determinista).
        
        Args:
            mentioned_level: Nivel mencionado en la query
            available_levels: Niveles disponibles en la tabla
            
        Returns:
            Nivel inmediatamente inferior, o None si no existe
        """
        # Buscar niveles menores que el mencionado
        lower_levels = [l for l in available_levels if l < mentioned_level]
        
        if not lower_levels:
            # No hay nivel inferior, usar el mínimo disponible
            return min(available_levels) if available_levels else None
        
        # Retornar el inmediatamente inferior
        return max(lower_levels)

    def _normalize_number(self, value) -> float:
        """
        Normaliza valores numéricos que vienen del LLM.
        MEJORA 2: Validación estricta de tipos.
        """
        # MEJORA 2: Validación estricta
        if not isinstance(value, (int, float, str)):
            raise ValueError(f"Tipo no soportado: {type(value)}")

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            v = value.strip()
            # Quitar separadores de miles y adaptar decimal europeo
            v = v.replace(".", "").replace(",", ".")
            m = re.search(r"-?\\d+(\\.\\d+)?", v)
            if not m:
                raise ValueError(f"No se encontró número en '{value}'")
            return float(m.group(0))

        raise ValueError(f"Tipo no soportado para valor numérico: {type(value)}")

    def extract_salary_data(
        self,
        table_content: str,
        query: str,
        company: str,
        year: int,
    ) -> Optional[SalaryData]:
        """
        Usa LLM para extraer datos relevantes de la tabla.
        MEJORA 1: Inferencia en Python
        MEJORA 2: Validación estricta
        MEJORA 3: Logging mejorado
        MEJORA 4: Modo simple query
        """
        # MEJORA 4: Detectar si es consulta simple
        q_lower = query.lower()
        is_simple = any(kw in q_lower for kw in ['cuanto cobra', 'cuánto cobra', 'salario de', 'salario del'])
        
        # MEJORA 1: Extraer niveles disponibles en Python
        available_levels = self._extract_levels_from_table(table_content)
        logger.info(f"Niveles disponibles en tabla: {available_levels}")
        
        # Extraer nivel mencionado en query
        level_match = re.search(r'nivel\s+(\d+)', query.lower())
        if not level_match:
            logger.warning(f"No se encontró nivel en query: {query}")
            return None
        
        mentioned_level = int(level_match.group(1))
        logger.info(f"Nivel mencionado en query: {mentioned_level}")
        
        # MEJORA 4: Si es consulta simple, solo extraer ese nivel
        if is_simple:
            logger.info("Consulta simple detectada: solo se extraerá el nivel mencionado")
            level_origin = mentioned_level
            level_destination = mentioned_level
            level_origin_label = f"Nivel {mentioned_level}"
            level_destination_label = f"Nivel {mentioned_level}"
        else:
            # MEJORA 1: Inferir nivel de comparación en Python
            inferred_level = self._infer_comparison_level(mentioned_level, available_levels)
            
            if inferred_level is None:
                # MEJORA 3: Logging para QA
                logger.warning(
                    f"No se pudo inferir nivel de comparación. "
                    f"Nivel mencionado: {mentioned_level}, Disponibles: {available_levels}"
                )
                return None
            
            logger.info(f"Nivel inferido para comparación: {inferred_level}")
            
            level_origin = inferred_level
            level_destination = mentioned_level
            level_origin_label = f"Nivel {inferred_level} (inferido)"
            level_destination_label = f"Nivel {mentioned_level}"
        
        # Ahora usar LLM SOLO para extraer valores numéricos
        prompt = f"""
Eres un asistente experto en análisis de tablas salariales.

TABLA SALARIAL:
{table_content}

TAREA:
Extrae SOLO los valores numéricos del salario base anual para:
- Nivel {level_origin}
- Nivel {level_destination}

RESPONDE EN JSON ESTRICTO:
{{
  "level_{level_origin}": número (solo el valor numérico),
  "level_{level_destination}": número (solo el valor numérico),
  "field_name": "salario base anual"
}}

EJEMPLO:
{{
  "level_3": 25000,
  "level_4": 28000,
  "field_name": "salario base anual"
}}

TU RESPUESTA DEBE SER SOLO UN JSON VÁLIDO, SIN EXPLICACIONES.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.0,
                },
            )

            logger.debug(f"Respuesta LLM extracción: {response.text}")
            data = json.loads(response.text)

            # MEJORA 2: Validación estricta del JSON
            key_origin = f"level_{level_origin}"
            key_dest = f"level_{level_destination}"
            
            if key_origin not in data or key_dest not in data:
                # MEJORA 3: Logging para QA
                logger.error(
                    f"Extracción incompleta. "
                    f"Query: {query}, Esperado: {key_origin}, {key_dest}, "
                    f"Recibido: {list(data.keys())}"
                )
                return None
            
            # MEJORA 2: Validación estricta de tipos
            if not isinstance(data[key_origin], (int, float, str)):
                logger.error(f"Formato inesperado en {key_origin}: {type(data[key_origin])}")
                return None
            
            if not isinstance(data[key_dest], (int, float, str)):
                logger.error(f"Formato inesperado en {key_dest}: {type(data[key_dest])}")
                return None

            # Normalizar números
            origin_value = self._normalize_number(data[key_origin])
            dest_value = self._normalize_number(data[key_dest])

            # Validar que son números válidos
            if origin_value <= 0 or dest_value <= 0:
                logger.error(
                    f"Valores extraídos no válidos: origin={origin_value}, destination={dest_value}"
                )
                return None

            return SalaryData(
                level_origin=origin_value,
                level_destination=dest_value,
                field_name=data.get("field_name", "salario base"),
                company=company,
                year=year,
                level_origin_label=level_origin_label,
                level_destination_label=level_destination_label,
                is_simple_query=is_simple,
            )

        except Exception as e:
            logger.error(f"Error extrayendo datos: {e}", exc_info=True)
            return None

    def calculate(self, data: SalaryData) -> Optional[CalculationResult]:
        """
        Cálculo matemático preciso en Python.
        MEJORA 4: Manejo de consultas simples.
        """
        try:
            origin = float(data.level_origin)
            destination = float(data.level_destination)

            # Validación de datos
            if origin <= 0 or destination <= 0:
                logger.error("Valores salariales deben ser positivos")
                return None

            # MEJORA 4: Si es consulta simple, no calcular diferencia
            if data.is_simple_query:
                return CalculationResult(
                    difference=0.0,
                    percentage=0.0,
                    level_origin_value=round(destination, 2),
                    level_destination_value=round(destination, 2),
                    field_name=data.field_name,
                    calculation_type="simple_query",
                )

            # Cálculos precisos
            difference = destination - origin
            percentage = (difference / origin) * 100 if origin > 0 else 0

            return CalculationResult(
                difference=round(difference, 2),
                percentage=round(percentage, 2),
                level_origin_value=round(origin, 2),
                level_destination_value=round(destination, 2),
                field_name=data.field_name,
                calculation_type="difference",
            )

        except Exception as e:
            logger.error(f"Error en cálculo: {e}", exc_info=True)
            return None

    def validate_result(
        self,
        data: SalaryData,
        result: CalculationResult,
        tolerance: float = 0.01,
    ) -> bool:
        """
        Valida que el resultado sea coherente.
        MEJORA 4: Skip validation para consultas simples.
        """
        try:
            # MEJORA 4: Skip validation para consultas simples
            if data.is_simple_query:
                logger.info("Consulta simple: validación omitida")
                return True

            # Check 1: Diferencia correcta
            expected_diff = data.level_destination - data.level_origin
            if abs(result.difference - expected_diff) > tolerance:
                logger.error(
                    f"Diferencia incorrecta: {result.difference} != {expected_diff}"
                )
                return False

            # Check 2: Porcentaje correcto
            expected_pct = (expected_diff / data.level_origin) * 100
            if abs(result.percentage - expected_pct) > tolerance:
                logger.error(
                    f"Porcentaje incorrecto: {result.percentage} != {expected_pct}"
                )
                return False

            # Check 3: Valores positivos
            if any(
                v < 0
                for v in [
                    result.level_origin_value,
                    result.level_destination_value,
                ]
            ):
                logger.error("Valores negativos detectados")
                return False

            # Check 4: Diferencia razonable
            if abs(result.difference) > (data.level_origin * 2):
                logger.warning(
                    f"Diferencia muy grande: {result.difference} "
                    f"(> 200% de {data.level_origin})"
                )

            logger.info(
                f"Validación OK: diff={result.difference}, pct={result.percentage}, "
                f"origen={data.level_origin}, destino={data.level_destination}"
            )
            return True

        except Exception as e:
            logger.error(f"Error en validación: {e}", exc_info=True)
            return False
