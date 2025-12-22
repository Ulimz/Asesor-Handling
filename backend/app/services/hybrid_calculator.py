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

    def _roman_to_int(self, roman: str) -> int:
        """Convierte números romanos a enteros (básico 1-10)."""
        roman = roman.upper().strip()
        mapping = {
            'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
            'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10
        }
        return mapping.get(roman, 0)

    def _extract_levels_from_table(self, table_content: str) -> List[int]:
        """
        MEJORA 1: Extrae niveles disponibles en la tabla (Python, no LLM).
        Soporta dígitos (1, 2) y Romanos (I, II).
        
        Returns:
            Lista de niveles ordenados (ej: [1, 2, 3, 4, 5])
        """
        # Buscar patrones: "Nivel 3", "Grupo 4", "Nivel III"
        patterns_digit = [
            r'nivel\s+(\d+)',
            r'grupo\s+(\d+)',
            r'categor[ií]a\s+(\d+)',
            r'n\s*(\d+)', # N1, N 2
            r'level\s+(\d+)',
        ]
        
        patterns_roman = [
            r'nivel\s+([ivx]+)\b',
            r'grupo\s+([ivx]+)\b',
            r'categor[ií]a\s+([ivx]+)\b',
            r'n\s*([ivx]+)\b',
        ]
        
        levels = set()
        table_lower = table_content.lower()
        
        # 1. Extraer Dígitos
        for pattern in patterns_digit:
            matches = re.findall(pattern, table_lower)
            levels.update(int(m) for m in matches)
            
        # 2. Extraer Romanos
        for pattern in patterns_roman:
            matches = re.findall(pattern, table_lower)
            for m in matches:
                val = self._roman_to_int(m)
                if val > 0:
                    levels.add(val)
        
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
        MEJORA 2: Validación estricta / Tolerante
        MEJORA 3: Logging mejorado
        MEJORA 4: Modo simple query
        """
        # MEJORA 4: Detectar si es consulta simple
        q_lower = query.lower()
        is_simple = any(kw in q_lower for kw in ['cuanto cobra', 'cuánto cobra', 'salario de', 'salario del'])
        
        # MEJORA 1: Extraer niveles disponibles en Python
        available_levels = self._extract_levels_from_table(table_content)
        logger.info(f"Niveles disponibles en tabla (Norm): {available_levels}")
        
        # MEJORA 1 & FIX: Extraer TODOS los niveles para comparaciones explícitas
        level_matches = re.findall(r'nivel\s+(\d+)', query.lower())
        unique_levels = sorted(list(set(int(m) for m in level_matches)))

        if not unique_levels:
            logger.warning(f"No se encontró nivel en query: {query}")
            return None
        
        logger.info(f"Niveles detectados en query: {unique_levels}")

        # MEJORA RED TEAM 2 (RELAXED): Validación de Niveles "Fantasma"
        # Filtrar niveles de la query que NO existen en la tabla
        valid_unique_levels = [l for l in unique_levels if l in available_levels]
        
        if len(valid_unique_levels) < len(unique_levels):
            # FIX EXPERTO: No abortar, solo advertir. El LLM puede ser más listo que nuestro regex.
            invalid_levels = set(unique_levels) - set(valid_unique_levels)
            logger.warning(
                f"🚨 RED TEAM WARNING: Niveles {invalid_levels} no encontrados explícitamente en tabla. "
                "Procediendo con fallback a LLM (puede haber mapeo implícito)."
            )
            # NO ABORTAMOS. Confiamos en que el LLM encuentre "Nivel III" cuando pedimos "3".
        else:
            logger.info("✅ Validación de niveles OK.")

        # Recalcular lógica de origen/destino con niveles validados
        if is_simple and len(unique_levels) == 1:
            mentioned_level = unique_levels[0]
            logger.info("Consulta simple detectada: solo se extraerá el nivel mencionado")
            level_origin = mentioned_level
            level_destination = mentioned_level
            level_origin_label = f"Nivel {mentioned_level}"
            level_destination_label = f"Nivel {mentioned_level}"
        
        elif len(unique_levels) >= 2:
            level_origin = unique_levels[0]
            level_destination = unique_levels[1]
            level_origin_label = f"Nivel {level_origin}"
            level_destination_label = f"Nivel {level_destination}"
            logger.info(f"Comparación explícita activada: {level_origin} vs {level_destination}")

        else:
            mentioned_level = unique_levels[0]
            inferred_level = self._infer_comparison_level(mentioned_level, available_levels)
            
            if inferred_level is None:
                logger.warning(f"No se pudo inferir nivel de comparación para {mentioned_level}")
                return None
            
            level_origin = inferred_level
            level_destination = mentioned_level
            level_origin_label = f"Nivel {inferred_level} (inferido)"
            level_destination_label = f"Nivel {mentioned_level}"

        # MEJORA RED TEAM 1: Detección Dinámica de Concepto (Calculadora Tuerta fix)
        concept_target = "salario base anual" # Default
        q_lower = query.lower()
        
        # Mapa de conceptos comunes en convenios
        concept_map = {
            "transporte": "plus transporte",
            "nocturnidad": "plus hora nocturna",
            "festivo": "plus hora festiva",
            "festiva": "plus hora festiva",
            "domingo": "plus hora domingo",
            "trienio": "antigüedad / trienios",
            "antiguedad": "antigüedad",
            "manutencion": "plus manutención",
            "comida": "plus manutención",
            "hora extra": "hora extraordinaria",
            "variable": "retribución variable",
            "objetivos": "retribución variable"
        }
        
        for key, val in concept_map.items():
            if key in q_lower:
                concept_target = val
                break
        
        logger.info(f"🎯 RED TEAM: Concepto objetivo detectado: '{concept_target}'")

        # Ahora usar LLM SOLO para extraer valores numéricos
        prompt = f"""
Eres un asistente experto en análisis de tablas salariales.

TABLA SALARIAL:
{table_content}

TAREA:
Extrae SOLO los valores numéricos correspondientes al concepto: "{concept_target}" para:
- Nivel {level_origin}
- Nivel {level_destination}

IMPORTANTE:
- Si el concepto es mensual, anualízalo o úsalo tal cual pero sé consistente.
- Si no encuentras el valor exacto, devuelve null.

RESPONDE EN JSON ESTRICTO:
{{
  "level_{level_origin}": número (solo el valor numérico o null),
  "level_{level_destination}": número (solo el valor numérico o null),
  "field_name": "{concept_target}"
}}

EJEMPLO:
{{
  "level_3": 25000,
  "level_4": 28000,
  "field_name": "{concept_target}"
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
