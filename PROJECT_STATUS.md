# Estado del Proyecto - Asistente Handling

## 🔄 Resumen de Estado
- **Fase Actual:** Estabilización y Refinamiento RAG.
- **Última Actualización:** 20 de Diciembre 2025.
- **Estado General:** Backend funcional en nube. IA conectada con capacidades avanzadas de tabla salarial.

## ✨ Funcionalidades Completadas Recientes
### 1. RAG Salary Intelligence
- **Inyección de Tablas Completas:** El sistema ahora inyecta una tabla Markdown con **todos los niveles salariales** del grupo del usuario en el contexto de la IA.
- **Corrección de Seeding:** Script `seed_from_structure.py` actualizado para parsear `level_values` correctamente.
- **Verificación:** Tests confirman que la IA recibe datos de todos los niveles para comparaciones.

### 2. Gestión de Perfiles
- **Prevención de Duplicados:** `POST /api/users/me/profiles` ahora rechaza la creación si ya existe un perfil para la misma empresa.
- **Limpieza:** Scripts de corrección ejecutados y eliminados.

## 🚧 Trabajo en Curso / Pendiente
- **Refinamiento RAG ("Chapa" vs Dato):**
    - [ ] Separar intenciones en `rag_engine.py` para distinguir entre petición de datos puros y consultas legales.
    - [ ] Eliminar instrucciones de "cálculo manual" en `prompts.py` cuando el dato ya existe en tabla.

## 📊 Métricas Clave
- **Frontend:** Next.js desplegado en Vercel (estable).
- **Backend:** FastAPI en Railway (estable).
- **Base de Datos:** PostgreSQL + PgVector (estable).
