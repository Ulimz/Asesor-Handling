## 📅 Fecha
2025-12-16

## ✅ Qué se ha completado recientemente (Sincronización)
1.  **Data Foundations (Backend)**:
    *   **Extracción de Salarios**: `extract_salary_tables.py` refinado para Iberia, Groundforce, Swissport, Menzies.
    *   **Seeding**: `seed_salary_tables.py` implementado con bucle multi-compañía.
    *   **Modelos**: `SalaryTable` poblado con datos reales del BOE.

2.  **Lógica y API**:
    *   Nuevos endpoints de metadatos: `/metadata/companies`, `/groups`, `/levels`.
    *   `CalculatorService` adaptado para usar datos de base de datos.

3.  **UX Dinámica (Frontend)**:
    *   **CascadingSelector**: Componente implementado para selección jerárquica (Empresa -> Grupo -> Nivel).
    *   **Persistencia**: Selección del usuario se guarda en su perfil (`salary_level` migrado a String).

4.  **IA Integrada**:
    *   **Chat Context**: El perfil del usuario (Empresa, Nivel) se inyecta en el prompt del sistema RAG.

5.  **Mantenimiento y Limpieza**:
    *   **Auditoría Profunda**: Generados reportes en `auditoria_resultados/`.
    *   **Limpieza de Documentación**: Archivos raíz (`GUIA_SOLUCION.md`, `DOCKER_SETUP.md`, etc.) movidos a `docs/active/`.
    *   **Backup**: Generado backup completo en `backups/backup_full_20251216_XXXX.zip`.

## 📝 Estado Actual
*   **Base de Datos**: Contiene datos reales de convenios y tablas salariales.
*   **Calculadora**: Totalmente dinámica, impulsada por datos del backend.
*   **Chat**: Contexto-consciente y con reglas de parentesco implementadas (`rag_engine.py`).
*   **Documentación**: Organizada en `docs/active/` siguiendo directrices MANTRA.

## ⚠️ Advertencias / Bloqueos
*   **Despliegue Pendiente**: El código está listo, falta subir a Railway/Vercel.

## 📋 Lista de Tareas Activas
- [ ] **Deploy to Production (Railway)**: Push a GitHub y verificar build.
- [ ] **Fix AI Kinship & Leave Logic**: (Verificado en código, falta test de campo).
- [ ] **Refine Prompt Structure**: (Verificado en código).
- [x] **System Backup**: Completado.
- [x] **Documentation Cleanup**: Completado.
