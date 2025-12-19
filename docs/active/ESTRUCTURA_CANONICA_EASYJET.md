# Estructura Canónica: EasyJet Handling Spain (Actualizado 2025)

## Fuente de Verdad
*   **Convenio**: V Convenio Colectivo EasyJet Handling Spain.
*   **Año Referencia**: **2025** (Tablas Salariales Anexo I).
*   **Análisis Artículos**: 21 (Grupos), 84-87 (Retribuciones, Pluses, Progresión), 33 (Perentorias).

---

## 1. Grupos Profesionales y Categorías (UX y Backend)

### Principio de Diseño
Para mantener la compatibilidad con el sistema de "3 niveles" (Company -> Group -> Level) y reflejar la realidad salarial donde *Jefes de Área* tienen salarios distintos según Tipo A, B o C, se ha definido la siguiente estructura:

*   **Group**: El Grupo Profesional del Convenio (Técnicos Gestores, Administrativos, Servicios Auxiliares).
*   **Level**: Combina la Categoría específica con el Nivel de progresión (Ej: "Jefe de Área Tipo A - Nivel 1").

### Desglose por Grupo

#### A. Técnicos Gestores
**Categorías Distintas**:
1.  **Jefe de Área Tipo A**:
    *   Salario Base 2025: **2.104,00 €**
    *   Plus Función Fijo: **523,98 €** (x12)
2.  **Jefe de Área Tipo B**:
    *   Salario Base 2025: **1.803,00 €**
    *   Plus Función Fijo: **448,48 €** (x12)
3.  **Jefe de Área Tipo C**:
    *   Salario Base 2025: **1.538,00 €**
    *   Plus Función Fijo: **374,46 €** (x12)

**Niveles de Progresión**: 1 al 7 (Tabla 3).

#### B. Administrativos
**Categorías Distintas**:
1.  **Agente Coordinador**:
    *   Salario Base 2025: **1.538,00 €**
    *   Ad Personam: **30,11 €** (x14)
2.  **Agente Administrativo**:
    *   Salario Base 2025: **1.538,00 €**
    *   Ad Personam: **30,11 €** (x14)
3.  **Auxiliar Administrativo**:
    *   Salario Base 2025: **1.345,00 €**
    *   Ad Personam: **0,00 €**
    *   *Nota*: Sin progresión (Nivel único).

**Niveles de Progresión**: 1 al 7 (Solo Agentes).

#### C. Servicios Auxiliares
**Categorías Distintas**:
1.  **Agente de Rampa** (Incluye variantes con funciones, gestionadas como Plus):
    *   Salario Base 2025: **1.538,00 €**
    *   Ad Personam: **30,11 €** (x14)
2.  **Auxiliar de Rampa**:
    *   Salario Base 2025: **1.345,00 €**
    *   Ad Personam: **0,00 €**
    *   *Nota*: Sin progresión (Nivel único).

---

## 2. Análisis Meticuloso de Conceptos Retributivos (Arts. 84-87)

### Conceptos Fijos (Tabla 1 y 3)

| Concepto | Periodicidad | Detalles | Importe 2025 |
| :--- | :--- | :--- | :--- |
| **Salario Base** | Mensual (x14) | Varía por Categoría (ver arriba) | 1.345€ - 2.104€ |
| **Plus Progresión** | Mensual (x14) | Vinculado al Nivel (1-7). Tabla 3. | N1: 0,00€<br>N2: 38,19€<br>N3: 71,03€<br>N4: 102,61€ (Tec/Aux) / 107,17€ (Admin)<br>N5: 134,18€ (Tec/Aux) / 145,04€ (Admin)<br>N6: 204,18€ (Tec/Aux) / 225,00€ (Admin)<br>N7: 285,47€ (Tec) / 284,92€ (Aux) / 306,78€ (Admin) |
| **Ad Personam** | Mensual (x14) | Fijo compensatorio ex-subrogados | 30,11€ |
| **Plus Función (Cat)** | Mensual (x12) | Fijo inherente a Jefes de Área | 374,46€ - 523,98€ |

### Conceptos Variables (Tabla 1, 2 y 4)

| Concepto (ID Interno) | Descripción UX | Unidad | Valor 2025 | Notas |
| :--- | :--- | :--- | :--- | :--- |
| `PLUS_HORA_EXTRA` | Hora Extraordinaria | Hora | **17,14 €** | Auxiliares: **16,15 €** |
| `PLUS_HORA_NOCTURNA` | Plus Nocturnidad (22-06h) | Hora | **1,89 €** | Igual para todos. |
| `PLUS_FESTIVO_DOMINGO` | Hora Festiva / Domingo | Hora | **2,85 €** | Igual para todos. |
| `PLUS_JOR_FRACCIONADA_1_12` | Jornada Partida (Días 1-12) | Día | **11,91 €** | Primer tramo mensual. |
| `PLUS_JOR_FRACCIONADA_13` | Jornada Partida (Días 13+) | Día | **18,25 €** | Segundo tramo mensual. |
| `PLUS_MADRUGUE` | Plus Madrugue (04:00-06:00) | Día | **8,10 €** | Por turno iniciado en banda. |
| `PLUS_TRANSPORTE` | Plus Transporte | Día | **4,95 €** | Aux Rampa: **4,50 €**. |
| `PLUS_HORA_PERENTORIA` | Hora Perentoria | Hora | **Variable** | Ver Tabla 4. Depende de Nivel/Grupo. (18,86€ a 33,77€) |
| `PLUS_COMP_FESTIVO` | Compensación Festivo | Festivo | **102,64 €** | Por no recuperar festivo trabajado. |
| `PLUS_JORNADA_IRREGULAR` | Plus Jornada Irregular | Mes | **175,94 €** | Art. 30. |

### Pluses Función Específicos (Tabla 2)

*   **Coordinador/Headset**: 128,15 € (x12)
*   **Conductor**: 128,15 € (x12)
*   **Supervisor**: 128,15 € (x12)
*   **Dos Funciones**: 237,56 € (x12)
*   **Jefe de Servicios**: 266,37 € (x12)
*   **Jefe Turno A/B/C**: 367,17 € / 215,97 € / 143,99 € (x12)

---

## 3. Estrategia de Implementación Técnica

1.  **JSON Estructurado**: Reflejará estas variaciones (especialmente Tabla 4 Perentorias).
2.  **Seeding Script**:
    *   Implementará lógica para `PLUS_HORA_PERENTORIA` leyendo un mapa de valores por Nivel.
    *   Distinguirá Auxiliares para `PLUS_HORA_EXTRA` y `PLUS_TRANSPORTE`.
    *   Añadirá los dos tramos de Jornada Fraccionada.

---
