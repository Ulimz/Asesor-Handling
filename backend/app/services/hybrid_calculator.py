"""
Calculadora Híbrida - Fase 2
LLM: Razonamiento y extracción
Python: Cálculo matemático preciso con guardrails
"""

import logging
import json
import re
from typing import Optional
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

    def to_dict(self) -> dict:
        return {
            "level_origin": self.level_origin,
            "level_destination": self.level_destination,
            "field_name": self.field_name,
            "company": self.company,
            "year": self.year,
            "level_origin_label": self.level_origin_label,
            "level_destination_label": self.level_destination_label,
        }


@dataclass
class CalculationResult:
    """Resultado del cálculo con metadata."""
    difference: float
    percentage: float
    level_origin_value: float
    level_destination_value: float
    field_name: str
    calculation_type: str  # "difference", "percentage", "total"

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
    """Calculadora con guardrail matemático."""

    def __init__(self, gemini_model):
        """
        Args:
            gemini_model: Instancia de genai.GenerativeModel
        """
        self.model = gemini_model

    def _normalize_number(self, value) -> float:
        """
        Normaliza valores numéricos que vienen del LLM.
        Soporta:
        - int / float
        - strings tipo "25.000,00", "25,000.00", "25000", "25k"
        """
        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            v = value.strip()
            # Quitar separadores de miles y adaptar decimal europeo
            v = v.replace(".", "").replace(",", ".")
            m = re.search(r"-?\d+(\.\d+)?", v)
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

        Args:
            table_content: Contenido de la tabla salarial
            query: Query del usuario
            company: Empresa
            year: Año

        Returns:
            SalaryData con valores extraídos o None si falla
        """
        prompt = f"""
Eres un asistente experto en análisis de tablas salariales.

TABLA SALARIAL:
{table_content}

QUERY DEL USUARIO:
{query}

TAREA:
Extrae los valores numéricos relevantes para responder la query.

IMPORTANTE - INFERENCIA INTELIGENTE:
1. Identifica los niveles mencionados en la query
2. **CASO ESPECIAL**: Si la query pide una diferencia/comparación ("cuánto más", "diferencia", "incremento") 
   pero SOLO menciona un nivel (ej: "Nivel 4"), ASUME que la comparación es con el nivel inmediatamente 
   inferior (ej: Nivel 3).
3. Si no existe nivel inferior, compara con el nivel 1 (base).
4. Extrae el salario base anual de cada nivel
5. Identifica el campo comparado (salario base, plus, etc.)

RESPONDE EN JSON ESTRICTO:

EJEMPLO DE SALIDA VÁLIDA:
{{
  "level_origin": 25000,
  "level_destination": 28000,
  "field_name": "salario base anual",
  "level_origin_label": "Nivel 3",
  "level_destination_label": "Nivel 4"
}}

EJEMPLO CON INFERENCIA (query: "cuánto más cobra nivel 4"):
{{
  "level_origin": 25000,
  "level_destination": 28000,
  "field_name": "salario base anual",
  "level_origin_label": "Nivel 3 (inferido)",
  "level_destination_label": "Nivel 4"
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

            # Validar claves obligatorias
            required_keys = ["level_origin", "level_destination"]
            for key in required_keys:
                if key not in data:
                    logger.error(f"Falta clave requerida en JSON: {key}")
                    return None

            # Normalizar números
            origin = self._normalize_number(data["level_origin"])
            destination = self._normalize_number(data["level_destination"])

            # Validar que son números válidos
            if origin <= 0 or destination <= 0:
                logger.error(
                    f"Valores extraídos no válidos: origin={origin}, destination={destination}"
                )
                return None

            return SalaryData(
                level_origin=origin,
                level_destination=destination,
                field_name=data.get("field_name", "salario base"),
                company=company,
                year=year,
                level_origin_label=data.get("level_origin_label", "nivel origen"),
                level_destination_label=data.get("level_destination_label", "nivel destino"),
            )

        except Exception as e:
            logger.error(f"Error extrayendo datos: {e}", exc_info=True)
            return None

    def calculate(self, data: SalaryData) -> Optional[CalculationResult]:
        """
        Cálculo matemático preciso en Python.

        Args:
            data: Datos extraídos por el LLM

        Returns:
            CalculationResult con cálculos precisos
        """
        try:
            origin = float(data.level_origin)
            destination = float(data.level_destination)

            # Validación de datos
            if origin <= 0 or destination <= 0:
                logger.error("Valores salariales deben ser positivos")
                return None

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

        Checks:
        1. Diferencia = destination - origin
        2. Porcentaje = (diferencia / origin) * 100
        3. Valores positivos
        4. Diferencia razonable (< 200% del origen) => warning
        """
        try:
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
