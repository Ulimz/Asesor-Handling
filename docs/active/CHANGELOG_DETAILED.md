# 📝 Registro Detallado de Cambios (Granular)

**Propósito**: Rastrear "al milímetro" cada cambio realizado en el proyecto (código, documentación, estructura) para mantener una memoria exacta del estado del sistema.
**Actualización**: OBLIGATORIA después de cada paso o comando relevante.

---

## 📅 Sesión: 16 Diciembre 2025

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
