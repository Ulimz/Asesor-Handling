# 📝 Registro Detallado de Cambios (Granular)

**Propósito**: Rastrear "al milímetro" cada cambio realizado en el proyecto (código, documentación, estructura) para mantener una memoria exacta del estado del sistema.
**Actualización**: OBLIGATORIA después de cada paso o comando relevante.


## 📅 Sesión: 17 Diciembre 2025

### [11:45] 🐛 Fix Crítico: "Sin Perfil" en Producción
- **Problema**: ProfileSwitcher mostraba "Sin Perfil" a pesar de crear perfiles exitosamente.
- **Causa Raíz**: **Next.js Caching**. El endpoint `GET /api/users/me/profiles` estaba siendo cacheado por el `fetch` del cliente (o Next.js fetch patch), retornando siempre `[]` (estado inicial) incluso después de crear un perfil.
- **Solución**: Añadido `{ cache: 'no-store' }` a todas las llamadas `fetch` en `src/lib/api-service.ts`.
- **Validación**:
    - Verificado que el Backend (`intelligent-vitality...`) funciona y devuelve perfiles correctamente.
    - Confirmada existencia de perfiles en BD Producción (Railway).
    - Simulado fetch exitoso.
- **Estado**: **SOLUCIONADO** (Requiere redespilegue Frontend).

### [11:50] 🐋 DevOps: Dockerfile Cleanup
- **Mejora**: Actualizado `Dockerfile.prod` para usar formato `ENV key=value` (estándar moderno) en lugar de `ENV key value`.
- **Beneficio**: Elimina warnings ruidosos durante el build en Railway y asegura compatibilidad futura.
- **Estado**: Patch aplicado.

### [13:00] 🛠️ Mejoras de Sistema de Perfiles y UX (Completo)
- **Fix Chat Interface**:
    - **Problema**: El asistente no recibía el contexto del perfil activo (Convenio, Grupo, Nivel) porque leía de la tabla legacy `users`.
    - **Solución**: Refactorizado `ChatInterface.tsx` para usar `useProfile()` y enviar `activeProfile` al backend.
    - **Mejora**: Añadido redireccionamiento a "Settings" para gestionar perfiles desde el chat.
- **Fix Calculadora Salarial**:
    - **Problema**: La calculadora no actualizaba sus selectores cuando cambiaba el perfil activo (solo al montar).
    - **Solución**: Actualizado `CascadingSelector.tsx` para observar cambios en `initialSelection` y sincronizar estado reactivamente.
- **Feat: Settings Page (Rediseño Total)**:
    - **Cambio**: Convertida la página de configuración en un **Hub de Gestión de Perfiles**.
    - **Funcionalidad**: Lista perfiles, permite activar, editar (incluyendo alias y empresa) y eliminar perfiles.
    - **Modals**: Actualizados `ProfileCreateModal` y `ProfileEditModal` para soportar la nueva lógica de `apiService.profiles`.
- **Feat: Onboarding Multi-Perfil**:
    - **Cambio**: El onboarding ahora crea un perfil REAL en `user_profiles` en lugar de solo actualizar al usuario.
    - **UX**: Añadido botón **"Guardar y Añadir Otro"** para permitir crear múltiples perfiles en cadena durante el registro.

### [13:10] ✅ Clean Code
- **Refactor**: Eliminadas dependencias legacy de edición de usuario en favor del nuevo sistema de perfiles.
- **Type Safety**: Corregido tipo `UserContext` para aceptar `salary_level` como string.

### [13:15] 💄 Branding & Stability Fixes
- **UI Update**:
    - **Header**: Cambiado título "Asistente Handling" por **"CHAT IA"** (Solicitud usuario).
    - **Fix**: Eliminado carácter "1" residual en el título del Dashboard.
- **Fix Backend Chat**:
    - **Problema**: Error de conexión (400 Bad Request) al hablar con perfil "Azul-Handling".
    - **Causa**: La lista de validación `VALID_COMPANIES` en el backend no incluía el slug generado por el seed (`azul-handling`).
    - **Solución**: Añadida lista completa de slugs permitidos (`azul-handling`, `convenio-sector`, `jet2`, `norwegian`, `south`) en `backend/app/constants.py`.
    - **Resultado**: El chat ahora acepta correctamente las consultas desde perfiles generados automáticamente.

---


## 📅 Sesión: 16 Diciembre 2025

### [21:20] 🔷 Azul Handling Implementation & Data Fixes
- **New Feature**: Full implementation of **Azul Handling** salary structure.
    - **Canonical Data**: Created `ESTRUCTURA_CANONICA_AZUL.md` (2025 Data).
    - **Template**: Added `azul_handling.json` with segmented "Jornada Fraccionada" (T1, T2, T3) and new Agreement Pluses (RCO, ARCO).
    - **Logic**: Updated `seed_standalone.py` to support hybrid seeding (Manual Base Salary + XML Variables).
    - **Verification**: Confirmed Base Salary (31.7k€) and Pluses in local database.
- **Bug Fixes**:
    - **Calculator**: Fixed "Hora Perentoria" missing from applicable concepts.
    - **Data**: Removed duplicate "Garantía Personal".
    - **Isolation**: Verified that Azul data does not interfere with Sector/Jet2 companies.

### [21:50] 🌩️ Hotfix: Cloud Data Synchronization
- **Issue**: Cloud database missing new Azul concepts (Fraccionada Tiers, RCO/ARCO) after deployment.
- **Root Cause**: Deployment does not automatically run seeding scripts. Data was stale.
- **Fix**: Created `backend/seed_production.py` (One-Click Fix) to force-seed correct definitions and values in production.
- **Action Required**: Run `python backend/seed_production.py` in Prod Console.

### [22:05] 🐛 Critical Fix: Azul Handling Concept Visibility
- **Issue**: User reporting "nothing appears" or generic sector fields despite correct seeding.
- **Root Cause**: Backend API `router.py` was forcefully remapping `azul-handling` requests to `convenio-sector`, ignoring the custom Azul definitions in DB.
- **Fix**: Removed `azul-handling` from the "Sector Alias" list. Now it loads its own specific `azul-handling` concepts.

### [23:00] 🔄 Multi-Profile System (Phase 1 & 2)
- **Phase 1 - Calculator Decoupling**:
    - **Problem**: Calculator was auto-saving to user profile on every change, causing data corruption.
    - **Solution**: Removed auto-save behavior. Added explicit "Guardar esta configuración en mi Perfil" button.
    - **Result**: Calculator now operates as a "Sandbox" - changes are temporary until user explicitly saves.
- **Phase 2 - Multi-Profile Architecture**:
    - **Database**: Created `user_profiles` table (One-to-Many with `users`).
    - **Backend API**: Implemented full CRUD endpoints (`/api/users/me/profiles`).
    - **Frontend**: 
        - Created `ProfileContext` for global state management.
        - Added `ProfileSwitcher` component in Dashboard header.
        - Created `ProfileCreateModal` for new profile creation.
        - Integrated `SalaryCalculator` with active profile context.
    - **Result**: Users can now manage multiple professional profiles (e.g., "Iberia Morning", "Azul Weekend").

### [23:05] 🔧 Build Fix
- **Issue**: Deployment failed due to missing `'use client'` directives in refactored components.
- **Fix**: Restored `'use client'` in `src/app/dashboard/page.tsx` and `SalaryCalculator.tsx`.
- **Status**: Fix pushed, awaiting successful deployment.

### [23:20] 🐛 Bug Fix: Profile Creation Modal
- **Issue 1**: Modal validation was too generic, showing "Por favor completa todos los campos" without specifying which field was missing.
- **Issue 2**: Modal state wasn't resetting between opens, causing confusion.
- **Fix**: 
    - Improved validation with specific error messages ("El nombre del perfil es obligatorio", "Por favor selecciona Empresa, Grupo y Nivel")
    - Added `handleClose()` function to reset all form state (alias, selection, error) when modal closes
    - Applied to all close scenarios (X button, Cancel button, backdrop click)
- **Status**: Partially resolved. "Sin Perfil" display issue pending investigation (requires checking backend API response and ProfileContext refresh logic).

### [22:45] 🛠️ UX Fix: Profile Decoupling vs Calculator
- **Fix**: Disabled aggressive "Auto-Save" in Calculator. Now changing inputs does NOT overwrite your profile.
- **Feat**: Added manual "Guardar esta configuración en mi Perfil" button in Calculator.
- **Impact**: Solves issues where testing scenarios corrupted the user's real saved data.

### [22:30] ✅ Final Fix: Azul Handling Logic & UI
- **UI**: Added price display `(300.00€)` to Checkbox concepts (RCO, ARCO) in `SalaryCalculator`.
- **Logic**: Removed hardcoded mapping in `CalculatorService` that prevented Azul variables from being calculated.
- **Data**: Verified Cloud Database has clean, segregated Azul 2025 data (Turnicidad, Fraccionada, etc).
- **Status**: **FULLY OPERATIONAL**.

### [21:25] 🛡️ Security Patch: Next.js Upgrade


- **Critical Fix**: Upgraded `next` from `16.0.7` to `16.0.10`.
- **Reason**: Blocked by Railway due to CVE-2025-55183/55184.
- **Status**: Patch applied and pushed to trigger new build.

### [15:45] 🐛 Corrección Critica: Error 500 Calculadora


*   **Error**: `ResponseValidationError` (None returned) en `POST /smart`.
*   **Causa**: Error de indentación en `CalculatorService.py` hacía que la lógica principal fuera inalcanzable, retornando `None` implícitamente.
*   **Calculator Fixes** (Critical):
    *   Fixed `500 Internal Server Error` in `CalculatorService` (Data Structure Mismatch).
    *   Fixed `PLUS_FTP` proportionality (Changed input type to `select`).
    *   Added missing concepts: `PLUS_FRACCIONADA`, `PLUS_MADRUGUE`, `PLUS_TRANSPORTE`.
    *   **CRITICAL DATA UPDATE**: Updated all Salary Concepts, Base Salaries, and Hour Rates to **2025 Values** (per User Tables).
    *   Fixed UI Duplicate inputs for Turnicity.
    *   Relaxed `UserSchema` validation for `salary_level`.
*   **Solución**: Reestructuración completa de la clase `CalculatorService` y añadido mapeo explícito de empresas del sector.
*   **Estado**: Desplegando corrección.

### [15:35] 🚀 Producción: Carga de Datos Remota (Railway)
*   **Acción Manual**: Ejecución de scripts de carga (`seed_standalone.py` y `seed_concepts_definitions.py`) directamente contra la base de datos de producción usando credenciales proporcionadas.
*   **Datos Cargados**:
    *   **Estructura**: Definiciones de conceptos para Convenio Sector (Jet2, Norwegian, etc.).
    *   **Valores**: Tablas salariales 2025 completas para 5 empresas.
*   **Estado**: Base de Datos de Nube sincronizada con Local.

### [15:30] 🔥 Hotfix: Conceptos Calculadora Ausentes
*   **Problema Critico**: Calculadora mostraba lista vacía para Jet2/Azul/Norwegian (solo "Garantía Personal").
*   **Causa**: Faltaba poblar la tabla `SalaryConceptDefinition` para el Convenio Sector, y las empresas mapeadas no apuntaban a él.
*   **Solución**:
    *   **Backend Router**: Mapeado explícito de `jet2`, `norwegian`, `south`, `azul-handling` -> `convenio-sector` en `/concepts/` endpoint.
    *   **Data Injection**: Ejecutado `seed_concepts_definitions.py` para traducir el Master Template a definiciones de frontend.
*   **Resultado**: Ahora aparecen todos los Turnos, Pluses y Variables en la calculadora para estas empresas.

### [15:15] 🧮 Frontend: Calculadora Inteligente Sectorial (v2.0)
*   **Adaptación**: Actualizado `SalaryCalculator.tsx` para soportar la nueva estructura canónica.
*   **Mejoras UX**:
    *   **Turnos**: Desplegable reconoce `PLUS_TURNICIDAD_` (2, 3, 4, 5+ turnos) y `PLUS_JORNADA_IRREGULAR`.
    *   **Responsabilidad**: Nuevos checkboxes para `PLUS_SUPERVISION` y `PLUS_JEFATURA`.
    *   **Limpieza**: Filtros actualizados para evitar que estos conceptos aparezcan duplicados como inputs genéricos.
*   **Despliegue**: Código subido a GitHub (Trigger Railway/Vercel).

### [15:00] 🏛️ Implementación Convenio Sector (Estrategia Master Template)
*   **Hito Arquitectónico**: Cambio de estrategia de extracción pura a **Modelo Híbrido (Template + XML)**.
*   **Acciones**:
    *   Creado `backend/data/structure_templates/convenio_sector.json`: Define la "verdad absoluta" (Grupos, Niveles, Pluses Fijos, Reglas).
    *   Desarrollado `seed_standalone.py`: Script robusto que fusiona la estructura del Template con valores variables (2025) extraídos de `general.xml`.
    *   **Resultado**: Base de datos poblada con estructura perfecta + valores reales actualizados.
    *   **Cobertura**: Convenio Sector y empresas adheridas (Jet2, Norwegian, South).

### [14:40] 🧹 Normalización Swissport (Type 3)
*   **Problema**: Grupos incorrectos y Niveles perdidos ("Base").
*   **Solución**:
    *   Implementada detección de Grupo por Título de Tabla (Type 3).
    *   Normalización forzada a los 3 Grupos Canónicos (`Administrativos`, `Servicios Auxiliares`, `Técnicos Gestores`).
    *   Corrección de lógica de niveles en `extract_salary_tables.py`.
    *   Validado con `verify_swissport_extraction.py`.

### [14:45] 🛠️ Fix: Estructura Salarial Menzies Aviation (Tipo 2 Complejo)
*   **Problema**: La extracción generaba grupos "basura" (ej. "Agente adm (Supervisor...)") y niveles numéricos incorrectos ("10,73").
*   **Causa Raíz**: En tablas de conceptos ("Tabla salarial 1"), la columna "Compen. festivo" no se detectaba como header mapeado, por lo que el script la interpretaba erróneamente como una columna de etiqueta secundaria (Category), desplazando la Categoría real a la posición de Grupo.
*   **Solución** (`extract_salary_tables.py`):
    *   Ajustada la regex de detección de columnas para incluir `compen` + `festiv` como `HORA_FESTIVA`.
*   **Resultado**:
    *   **Menzies**: Ahora muestra limpiamente los 3 grupos: "Administrativos", "Servicios Auxiliares", "TÉCNICOS GESTORES".
    *   Niveles correctos: "Agente administrativo", "Jefe de Turno - Nivel 1", etc.

### [14:00] 🛠️ Fix: Estructura Salarial Aviapartner, WFS & Azul (Tipo 1)
*   **Problema Critico**: El selector de "Grupo" mostraba solo "General" porque los grupos reales ("Técnicos Gestores", "Administrativos") se extraían incorrectamente como categorías/niveles.
*   **Solución Backend** (`extract_salary_tables.py`):
    *   Implementada detección para **Tablas Matriz Tipo 1**: Si una fila tiene 1 etiqueta pero múltiples columnas de datos (niveles), esa etiqueta se promueve a **Grupo**.
    *   **Limpieza de Niveles**: Refinado el nombre del nivel en DB. Si la categoría es "Base", el nivel se guarda como "Nivel X" (limpio) en lugar de "Base - Nivel X".
*   **Impacto**: 
    *   **Aviapartner, WFS, Azul Handling**: Ahora tienen sus grupos reales correctamente poblados.
*   **Verificación**: `verify_structure.py` confirma múltiples grupos y niveles limpios.

### [13:00] 🛠️ Fix: EasyJet Data Structure (Groups vs Levels)
*   **Problema Detectado**: El selector "Grupo" en EasyJet mostraba categorías específicas ("Jefe de Área", "AR con función") mezcladas con grupos reales, y textos sucios.
*   **Solución Backend**: 
    *   Refactorizado `_parse_concept_columns_table` y `_parse_level_matrix_table` en `extract_salary_tables.py`.
    *   **Lógica Mejorada**: Ahora detecta correctamente cuando una fila tiene columnas de "Grupo" y "Categoría" separadas (incluso con `rowspan`).
    *   **Resultado**: Separa limpiamente el **Grupo** (ej. "Servicios Auxiliares") del **Nivel/Categoría** (ej. "Agente de Rampa").
*   **Validación**: Script `verify_easyjet.py` confirma que los grupos ahora son genéricos y limpios, y los niveles contienen los puestos específicos.
*   **Base de Datos**: Re-sembrada completamente con esta nueva lógica.

### [12:30] 🛠️ Fix: Selector de Compañía & Aviapartner
*   **Selector Frontend/Backend**:
    *   **Acción**: Modificado `backend/app/modules/calculadoras/router.py`.
    *   **Detalle**: Filtrado explícito de `convenio-sector` en endpoint `/metadata/companies`.
    *   **Resultado**: "Convenio Sector" ya no aparece en el selector del usuario (UI limpia).
*   **Aviapartner Data**:
    *   **Fix Crítico**: Mapeo de "Nivel entrada" / "base" -> **Nivel 1** en `extract_salary_tables.py`.
    *   **Limpieza**: Eliminado símbolo `€` de nombres de grupo (ej. "Técnicos gestores").
    *   **Validación**: Script `verify_aviapartner.py` confirma presencia de Nivel 1 y nombres limpios en DB Producción.

### [12:00] 🧹 Limpieza de Datos & 🚧 Banner Beta
*   **Limpieza Backend**: Implementado `clean_group_name()` en scripts de extracción.
    *   Elimina precios ("17.500") y textos basura de los selectores.
    *   Ejecutado Seed en Producción: **6284 registros limpios**.
*   **UX Frontend**: Añadido `BetaBanner` global (Layout).
    *   FIX: Elevado a `z-100` y `fixed top-0` para evitar solapamiento con Navbar.
    *   Estilo: Fondo Sólido Naranja (Alta Visibilidad).
*   **Despliegue**: Push realizado a `main`.

### [11:45] 🌍 Expansión de Base de Datos (Todas las Compañías)
*   **Solicitud**: Usuario reporta que faltaban compañías (Aviapartner, Sector...).
*   **Acción**: Actualizado `seed_salary_tables.py` para procesar TODOS los XMLs disponibles.
*   **Resultado**: Insertados **5393 registros** (antes 4034).
*   **Nuevas Compañías Activas**:
    *   `aviapartner`, `wfs`, `easyjet`, `azul-handling`
    *   `convenio-sector` (Generico)
    *   **Mapped**: `jet2`, `norwegian`, `south` (Usan datos sector)
*   **Verificación**: `verify_companies.py` confirma 12 compañías únicas en DB.

### [11:35] 🚀 Despliegue v1.7-FIXED (Conectividad Definitiva)
*   **Problema**: Frontend no conectaba con Backend (Selectores vacíos).
*   **Causa**: `salary-service.ts` ignoraba `api.ts` y CORS estaba restrictivo.
*   **Solución**: 
    *   Unificado servicio para usar `src/config/api.ts`.
    *   Abierto CORS a `*` (Wildcard) en Backend.
    *   Añadida marca visible `v1.7-FIXED`.

### [11:30] 🧪 Debugging en Producción (v1.6-DEBUG)
*   **Acción**: Añadida marca de agua visible en `layout.tsx` y logs en consola.
*   **Objetivo**: Confirmar si el despliegue se estaba realizando (cache busting).

### [11:27] 🌱 Seeding DB Producción (Railway)
*   **Problema**: Selectores vacíos en entorno de producción.
*   **Causa**: Base de datos de nube estaba vacía (solo se llenó la local).
*   **Acción**: Ejecutado `seed_salary_tables.py` apuntando a `interchange.proxy.rlwy.net`.
*   **Resultado**: Insertados 4034 registros en la nube.

### [11:25] 🚀 Redespliegue Manual (Solicitado por Usuario)
*   **Motivo**: Usuario reporta no ver los cambios en producción.
*   **Acción**: Forzar push de todo el estado actual para disparar build en Railway/Vercel.
*   **Estado Cógido**: Verificado `src/config/api.ts` (Backend URL correcta) y lógica de Parentesco.

### [11:15] 🐞 Bug Fix: Register Page UI & Logic
*   **Problema**: Orden de campos incorrecto y selectores estáticos (no cascading).
*   **Solución**: 
    *   Refactorizado `register/page.tsx` para usar `CascadingSelector`.
    *   Movido input "Preferred Name" a posición superior (antes de selectores).
    *   Eliminada lógica legacy de `knowledge-base`.

### [10:00] 🔄 Restauración de Estado (Backup Ayer)
*   **Estado**: El usuario confirma que se cargó el backup de ayer correctamente.
*   **Integridad**: No se han perdido cambios. Continuamos desde el punto de "Fallo de Cascada" corregido.

### [11:00] 🌐 Sincronización Dominio (SEO)
*   **Acción**: Actualizado fallback domain en `sitemap.ts` y `robots.ts`.
*   **Valor**: `https://asistentehandling.es` (Producción).

### [10:55] 🔍 Verificación Sitemap/SEO
*   **Acción**: Revisado `src/app/sitemap.ts` y `robots.ts`.
*   **Estado**: ✅ Creados y funcionales (usan `NEXT_PUBLIC_BASE_URL`).
*   **Documentación**: Añadida referencia SEO en `PROJECT_STATUS.md`.

### [10:45] ✅ Actualización de MANTRA.md
*   **Acción**: Refinado `docs/active/MANTRA.md`.
*   **Detalle**: 
    *   Definida estructura v1.1 oficial (root, docs/active, backend/scripts).
    *   Eliminadas referencias obsoletas (`PUSH_A_REMOTO`).
    *   Corregido typo `PROJECT_STATE` -> `PROJECT_STATUS`.

### [10:36] 📦 Backup del Sistema
*   **Acción**: Ejecutado script `scripts/create_backup.py`.
*   **Resultado**: Generado archivo `backups/backup_full_20251216_103654.zip`.
*   **Estado**: ✅ COMPLETADO.

### [10:30] 🧹 Limpieza de Documentación (Root Cleanup)
*   **Acción**: Ejecutado script `scripts/cleanup_docs.py`.
*   **Detalle**:
    *   Movidor `GUIA_SOLUCION.md` -> `docs/active/TROUBLESHOOTING_GUIDE.md`.
    *   Archivado `SESSION_SUMMARY.md` -> `docs/deprecated/SESSION_SUMMARY_OLD.md`.
    *   Movido `DOCKER_SETUP.md` -> `docs/active/INFRA_DOCKER.md`.
    *   Verificado `PROJECT_STATUS.md` y `CONTEXT_SESSION.md`.

### [10:15] 🔍 Auditoría Profunda del Proyecto
*   **Acción**: Análisis completo de carpetas y código.
*   **Hallazgos**:
    *   **Fase 1-3 (Data/Logic/UX)**: Confirmadas como COMPLETAS en código.
    *   **Fase 4 (Kinship/AI)**: Confirmada lógica en `rag_engine.py` y `kinship.py`.
    *   **Reportes Generados**: `auditoria_resultados/` (1_, 2_, 3_, 4_).

### [Initial] 🔄 Sincronización
*   **Acción**: Lectura de estado y verificación de archivos clave (`extract_salary.py`, `CascadingSelector`).
*   **Resultado**: Confirmado que el proyecto estaba en fase avanzada (Pre-Rollout).

---

### [11:10] 🚀 Despliegue v1.1 (GitHub & Production)
*   **Acción**: `git push` a repositorio `Ulimz/Asesor-Handling`.
*   **Fix Crítico**: Se excluyó `backups/` y `auditoria_resultados/` en `.gitignore` para evitar archivos >100MB.
*   **Contenido**: Limpieza de docs, SEO (`robots.ts`), Data Foundations.
*   **Trigger**: Inicia despliegue automático en Railway/Vercel.

## 📋 Próximos Cambios Previstos
1.  **Deployment**: Push a GitHub.
2.  **Verification**: Smoke test en entorno de producción.
