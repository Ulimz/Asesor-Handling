# Contexto de Sesión - 20 de Diciembre 2025

## ✅ Logros de Hoy
1.  **RAG Salary Comparisons (Backend Fix):**
    *   **Problema:** La IA no tenía "visión global" de los salarios, solo conocía el nivel del usuario.
    *   **Solución:** Se implementó `CalculatorService.get_group_salary_table_markdown` que inyecta la tabla completa (todos los niveles) en el contexto de la IA.
    *   **Resultado:** La IA ahora puede comparar niveles ("Diferencia Nivel 1 vs 2") con precisión, usando datos reales de la BD.

2.  **Prevención Duplicados de Perfil:**
    *   **Problema:** Se podían crear múltiples perfiles para la misma empresa.
    *   **Solución:** Se añadió validación en `router.py` (POST /me/profiles) que impide crear un nuevo perfil si ya existe uno activo para ese `company_slug`.

3.  **Análisis de "Verbosity" de la IA:**
    *   **Problema:** La IA explica demasiado y calcula a mano en lugar de dar el dato directo.
    *   **Causa:** Conflicto en prompts ("Actúa como experto" vs "Usa la tabla") y orden explícita de "REALIZA EL CÁLCULO".
    *   **Próximo Paso:** Separar intenciones (`SALARY_DATA` vs `SALARY_CONSULT`) para respuestas directas.

## 📝 Estado Actual
- **Código:** Todo lo anterior pusheado a `main` y desplegado en nube.
- **Base de Datos:** Seeding corregido para guardar bien los valores por nivel.

## 🔜 Siguientes Pasos (Mañana)
1.  **Refinar Prompt RAG:** Implementar el "Modo Dato" para respuestas concisas.
2.  **Frontend:** Verificar que los perfiles duplicados ya no afecten la UI.
