# Análisis Profundo de Estructura Salarial por Compañía

**Fecha**: 16 de Diciembre 2025
**Estado**: Completado
**Objetivo**: Documentar la estructura exacta de las tablas salariales en los archivos XML de cada compañía para guiar la refactorización de los extractores y corregir el bug "Grupo: General" en la UI.

---

## 1. Resumen de Patrones Detectados

Hemos identificado 3 patrones principales en la estructura de los convenios (XML):

| Tipo | Descripción | Compañías Afectadas | Estado Actual en UI |
| :--- | :--- | :--- | :--- |
| **Tipo 1** | **Columna 0 = Grupo**. Niveles en columnas (1-7). | **Aviapartner, WFS, Azul Handling** | ❌ Fallo Principal (Grupo: General) |
| **Tipo 2** | **Columna 0 = Grupo (Rowspan)** + Col 1 = Categoría. | **Menzies**, Groundforce, EasyJet | ⚠️ Parcialmente Funcional / Corregido |
| **Tipo 3** | **Grupo en Título de Tabla**. Niveles en Filas. | **Swissport** | ❌ Fallo (Grupo: General) |

---

## 2. Análisis Detallado por Compañía

### 2.1. Aviapartner
*   **Archivo**: `aviapartner.xml`
*   **Patrón**: Tipo 1 (Matriz de Niveles Simple).
*   **Estructura Visual**:
    ```text
    | Grupo Laboral      | Nivel entrada | Nivel 2 | ... | Nivel 7 |
    |--------------------|---------------|---------|-----|---------|
    | Técnicos gestores  | 1.200 €       | 1.300 € | ... | ...     |
    | Administrativos    | 1.100 €       | ...     | ... | ...     |
    | Serv. Auxiliares   | 1.000 €       | ...     | ... | ...     |
    ```
*   **Problema**: El extractor actual interpreta "Técnicos gestores" como una *Categoría* dentro del grupo por defecto "General".
*   **Solución Requerida**: Mapear `Columna 0` -> `group`. Mapear `Header Columna X` -> `level`.

### 2.2. Grupo WFS
*   **Archivo**: `wfs.xml`
*   **Patrón**: Tipo 1 (Matriz de Niveles Simple).
*   **Estructura Visual**: Idéntica a Aviapartner.
*   **Grupos Identificados**: "Técnicos gestores", "Administrativos", "Serv. Auxiliares".
*   **Problema**: Mismo que Aviapartner. Aparece todo bajo "General".
*   **Solución Requerida**: Misma lógica que Aviapartner.

### 2.3. Azul Handling
*   **Archivo**: `azul.xml` (Líneas 893+)
*   **Patrón**: Tipo 1 (Matriz de Niveles Simple).
*   **Estructura Visual**: Idéntica a Aviapartner/WFS.
*   **Grupos Identificados**: "Técnicos gestores.", "Administrativos.", "Serv. Auxiliares.".
*   **Observación**: Tiene tablas adicionales de plures ("Tabla horas perentorias", "Tabla conceptos artículo 26").
*   **Solución Requerida**: Misma lógica que Aviapartner para la tabla principal.

### 2.4. Menzies Aviation
*   **Archivo**: `menzies.xml`
*   **Patrón**: Tipo 2 (Matriz con Grupo y Categoría).
*   **Estructura Visual**:
    ```text
    | Grupo             | Categoría            | Nivel 1 | Nivel 2 | ... |
    |-------------------|----------------------|---------|---------|-----|
    | TÉCNICOS GESTORES | Jefe de Área tipo A  | ...     | ...     | ... |
    |                   | Jefe de Área tipo B  | ...     | ...     | ... |
    ```
    *Nota: La columna "Grupo" suele usar `rowspan`.*
*   **Problema Potencial**: Si el extractor no maneja bien el `rowspan` o las 2 columnas de etiquetas, fallará o mezclará datos.
*   **Estado**: Recientemente se mejoró `_parse_level_matrix_table` para soportar esto (fix de EasyJet), por lo que Menzies podría estar cerca de funcionar si se re-procesa.

### 2.5. Swissport
*   **Archivo**: `swissport.xml`
*   **Patrón**: Tipo 3 (Grupo Implícito en Título).
*   **Estructura Visual**:
    *   *Título*: "Tabla Salarial Agentes Administrativos"
    *   *Tabla*:
        ```text
        | Nivel      | Salario Base | ... |
        |------------|--------------|-----|
        | Nivel 1    | 15.000 €     | ... |
        | Nivel 2    | 16.000 €     | ... |
        ```
*   **Problema**: La tabla NO tiene columna de Grupo. El grupo está en el texto `p` anterior a la tabla. El extractor actual lo ignora y pone "General".
*   **Solución Requerida**: El extractor debe leer el nodo anterior (`prev_node`) o el título de la tabla para extraer el Grupo ("Agentes Administrativos").

### 2.6. Groundforce
*   **Archivo**: `groundforce.xml` (Líneas 1105+)
*   **Patrón**: Tipo 2 (Grupo + Categoría).
*   **Estructura**:
    *   Columnas: `Grupo` (con rowspan) | `Categorías` | `T. anual` | `S. base`...
*   **Estado**: Tiene un extractor dedicado (`extract_groundforce_salaries`). Debería funcionar bien, asumiendo que el extractor busca explícitamente estas columnas.

### 2.7. Iberia
*   **Archivo**: `iberia.xml`
*   **Patrón**: Custom / Secciones.
*   **Estado**: Tiene extractor dedicado robusto (`extract_iberia_salaries`) que busca encabezados como "TIERRA" y "VUELO". No se esperan problemas graves de estructura "General", aunque siempre es bueno verificar.

---

## 3. Plan de Acción Recomendado (Lógica de Código)

Para arreglar la UI y que los selectores funcionen ("Compañía" -> "Grupo" -> "Nivel"), debemos ajustar `backend/scripts/extract_salary_tables.py`:

1.  **Refactorizar `_parse_level_matrix_table`**:
    *   **Detección de Tipo 1 (Aviapartner/WFS/Azul)**:
        *   Si hay headers de niveles ("Nivel 1", "Nivel entrada"...) Y solo 1 columna de etiqueta:
        *   Esa columna de etiqueta es el **GRUPO**.
        *   La **CATEGORÍA** (nivel en DB) será "Base" o similar, mapeada internamente al número de nivel (1..7).
    *   **Detección de Tipo 2 (Menzies/EasyJet)**:
        *   Ya soportado (2 columnas de etiquetas). Asegurar que la Columna 0 vaya a `group` y Columna 1 a `level` (nombre de categoría).

2.  **Refactorizar Extracción de Swissport (Tipo 3)**:
    *   Modificar la lógica para buscar el nombre del grupo en el párrafo inmediatamente anterior a la tabla si la tabla no tiene columnas de grupo explícitas pero sí filas de "Nivel X".

3.  **Limpieza de Datos**:
    *   Asegurar que nombres como "Técnicos gestores." (con punto) se limpien a "Técnicos Gestores".

4.  **Verificación**:
    *   Ejecutar `seed_salary_tables.py` solo para estas compañías.
    *   Verificar en DB (`SELECT DISTINCT "group" FROM salary_tables WHERE company_id = 'aviapartner'`).
