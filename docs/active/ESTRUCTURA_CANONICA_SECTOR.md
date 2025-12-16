# Estructura Canónica del Sector Handling (Referencia Maestra)

**Documento Vivo**: Define la estructura estándar de Grupos, Niveles y Conceptos Salariales basada en el V Convenio Colectivo General (BOE).
**Objetivo**: Servir de "plantilla maestra" para normalizar los datos de todas las empresas en la base de datos y simplificar la UX.

---

## 1. Grupos Profesionales (Simplificado)

Para la UX (Selectores), solo existirán estos 3 Grupos Principales. Cualquier sub-variante debe mapearse internamente a uno de estos:

1.  **Administrativos**
2.  **Servicios Auxiliares**
3.  **Técnicos Gestores**

---

## 2. Niveles y Categorías (Selector Secundario)

Cada Grupo tiene sus propios niveles o categorías. Estos son los que el usuario seleccionará en el segundo drop-down.

### 2.1 Grupo Administrativos
*   **Agente Administrativo** (Ejecución/Supervisión) -> Niveles 1 al 7
*   **Jefe Administrativo** (Mando) -> Niveles propios o salarios específicos.

### 2.2 Grupo Servicios Auxiliares
*   **Agente de Servicios Auxiliares** (Ejecución/Supervisión) -> Niveles 1 al 7
*   **Agente Jefe de Servicios Auxiliares** (Mando)

### 2.3 Grupo Técnicos Gestores
*   Niveles 1 al 7 (Generalmente)

> **Nota de UX**: En el selector de "Nivel/Categoría", mostraremos strings combinados si es necesario para claridad, ej: "Agente Administrativo - Nivel 3".

---

## 3. Conceptos Retributivos (Estructura Calculadora)

La calculadora debe distinguir entre conceptos fijos (mensuales) y variables (por hora/día).

### 3.1 Conceptos Fijos (Selectores "Sí/No" o Cantidad Mensual)
Estos conceptos se añaden al salario base mensual si el usuario cumple la condición.

| Concepto | ID Interno (Sugerido) | Valor Base (2025) | Regla de Aplicación | Artículo Convenio |
| :--- | :--- | :--- | :--- | :--- |
| **Plus de Jornada Irregular** | `PLUS_JORNADA_IRREGULAR` | 142.12 € | Fijo mensual si aplica jornada irregular. Incompatible con Turnicidad/FTP. | Art 28.10 |
| **Plus Turnicidad (2 Turnos)** | `PLUS_TURNICIDAD_2` | 81.99 € | Si realiza 2 turnos/mes. | Art 28.11 |
| **Plus Turnicidad (3 Turnos)** | `PLUS_TURNICIDAD_3` | 109.32 € | Si realiza 3 turnos/mes. | Art 28.11 |
| **Plus Turnicidad (4 Turnos)** | `PLUS_TURNICIDAD_4` | 125.72 € | Si realiza 4 turnos/mes. | Art 28.11 |
| **Plus Turnicidad (5+ Turnos)** | `PLUS_TURNICIDAD_5` | 142.12 € | Si realiza 5+ turnos/mes. | Art 28.11 |
| **Plus Supervisión** | `PLUS_SUPERVISION` | 76.53 € | Mensual. Proporcional a jornada. | Art 28.12 |
| **Plus Jefatura** | `PLUS_JEFATURA` | 131.90 € | Mensual. Proporcional a jornada. | Art 28.12 |
| **Plus FTP** | `PLUS_FTP` | Max 98.39 € | Proporcional a % jornada. Incompatible con Irregular/Turnicidad. | Art 28.13 |

### 3.2 Conceptos Variables (Inputs Numéricos: Horas/Días)
Estos dependen de la actividad real del mes.

| Concepto | ID Interno (Sugerido) | Valor Base (2025) | Unidad | Artículo |
| :--- | :--- | :--- | :--- | :--- |
| **Plus Nocturnidad** | `PLUS_NOCTURNIDAD` | 1.61 € | Hora (22:00 - 06:00) | Art 28.1 |
| **Hora Extraordinaria** | `HORA_EXTRA` | (Anual/1712)*1.5 | Hora | Art 28.2 |
| **Hora Perentoria** | `HORA_PERENTORIA` | (Anual/1712)*1.75 | Hora | Art 28.3 |
| **Hora Festiva** | `HORA_FESTIVA` | 2.85 € | Hora trabajada en festivo | Art 28.4 |
| **Hora Domingo** | `HORA_DOMINGO` | 2.80 € | Hora trabajada en domingo | Art 28.5 |
| **Jornada Fraccionada** | `PLUS_FRACCIONADA` | 11.34 € | Día | Art 28.6 |
| **Plus Madrugue** | `PLUS_MADRUGUE` | 6.43 € | Día (Inicio 04:00-06:55) | Art 28.7 |
| **Plus Transporte** | `PLUS_TRANSPORTE` | 2.83 € | Día trabajado | Art 28.8 |
| **Ayuda Manutención** | `AYUDA_MANUTENCION` | 6.43 € | Día (Según horario comidas) | Art 28.9 |
| **Garantía Personal (Ad Personam)** | `PLUS_AD_PERSONAM` | (Manual) | Euros (Valor Fijo) | - |

---

## 4. Estrategia de Implementación en Backend

1.  **Extracción Normalizada**:
    *   Al procesar cualquier XML, el **Grupo** debe normalizarse a uno de los 3 canónicos.
    *   Ej: "Agentes Administrativos H24" -> Grupo: `Administrativos`, Nivel: `Agente H24 - Nivel X`.

2.  **Base de Datos**:
    *   Asegurar que los conceptos variables (Hora Extra, Nocturnidad) se guarden como registros en `salary_tables` con claves estandarizadas (ej: `HORA_EXTRA_VALUE`, `NOCTURNIDAD_VALUE`) asociados al Grupo/Nivel correspondiente, para que la calculadora pueda hacer `SELECT value FROM salary_tables WHERE group='...' AND level='...' AND concept='NOCTURNIDAD'`.
