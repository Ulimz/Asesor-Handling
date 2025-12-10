# Contexto de Sesión: Integridad de Datos y Especialización IA

## 📅 Fecha
2025-12-10

## ✅ Qué se hizo hoy (Actualizado)
1.  **Backend & Base de Datos**:
    *   **Autenticación**: Creada tabla `users`, endpoint `/api/users/login` y verificado login JWT.
    *   **Integridad de Datos**: Descubierto que `convenios` estaba vacía. Creado script `seed_convenios.py` y poblada con 8 empresas reales.
    *   **API Key**: Actualizada Google API Key (la anterior daba error 400).
    *   **Bug Fix**: Corregido error `name 'prompt' is not defined` en `rag_engine.py`.
2.  **Frontend & UI**:
    *   **Dashboard**: Arreglado selector de empresa (ya muestra Iberia, Azul, etc.).
    *   **Chat Rendering**: Implementado `react-markdown` + `remark-gfm` en `MessageBubble.tsx`. Las tablas ahora se renderizan perfectamente en lugar de texto plano.
## 📝 Current Session Status
**Achievements:**
- **Solved Critical Login Bug**: Fixed `PyJWT` subject type error (int vs str). Login now works perfectly.
- **Frontend Onboarding Complete**:
    - Multi-step wizard implemented.
    - Fixed "Empty Company List" bug by seeding DB and fixing `slug` mapping.
    - **Smart Company Management**: Added `slug` column to DB. Renamed "Iberia" to "South (Iberia)". Added Jet2, Norwegian.
- **User Profile Refining**:
    - Updated contract types (Fijo TP, etc.).
    - Removed irrelevant "Antigüedad" field.
    - Increased Salary Level max to 25.
- **Chat Personalization & RAG Context**:
    - Chat now greets user by name.
    - **Context Injection**: Frontend now sends User Profile (Level, Group) to Backend.
    - **Smart RAG**: Backend Prompt updated to use User Profile for answers (e.g. "Use Level 3 data").
    - **Table Priority**: Instructed AI to prioritize Table Lookups over manual calculations.
    - **Expanded Scope**: Added synonyms ("Descanso" -> "Jornada 12h") and increased chunk limit to find Statute answers.
- **UX/UI Polishing**:
    - Added "Close/Exit" button to Settings.
    - **Layout Fixes**: Added padding to Dashboard to prevent card clipping.
    - **Table Overflow**: Fixed horizontal scroll for large Salary Tables using `min-w-0` and `max-w-full`.

**Current Status:**
Phase 2 (Frontend & Profile) is **COMPLETED**, including advanced RAG Context features.

**Next Steps (Tomorrow):**
- **Phase 3: Intelligent Calculator**.
    - Structure Salary Tables in SQL (now AI reads them from text, but Calculator needs structured data).
    - Implement Logic for "Nómina Calculator".
- **Deployment Prep**: Tests are passing, but we should run a full E2E test soon.

**Warnings:**
- **RAG Synonyms**: The synonyms logic in `rag_engine.py` is hardcoded. Consider moving to a config file eventually.
- **Table Formatting**: `MessageBubble` table rendering is delicate. `whitespace-nowrap` is needed for readability but requires careful overflow handling.
*   **UI**: Limpia, tablas con scroll horizontal.
*   **Seguridad**: Backup de Fase 0 realizado (DB + Git Branch).

## ⚠️ Advertencias para Mañana
*   **No tocar `main` sin backup**: Vamos a entrar en modificaciones profundas de base de datos (`User` model). Trabajar siempre en `feature/user-profile-v2`.
*   **Calculadora**: Dependerá de que seamos capaces de estructurar las Tablas Salariales en BD.

## 📋 Lista de Tareas (Fase 2 - Perfil de Usuario)
- [ ] **Backend**: Actualizar modelo Usuario (Nivel, Contrato, Empresa).
- [ ] **Frontend**: Crear Wizard de Onboarding.
- [ ] **Settings**: Pantalla para editar perfil.
- [ ] **Calculadora**: Conectarla con los datos del perfil.
