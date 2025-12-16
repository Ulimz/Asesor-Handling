# 📊 Estado del Proyecto (Asistente_Handling)

Este documento resume el propósito, arquitectura y estado actual del proyecto. Debe revisarse al inicio de cada sesión para mantener el contexto.

## 🎯 Propósito
**Asistente_Handling** es una aplicación legal modular diseñada para trabajadores del sector handling aeroportuario en España. Su objetivo es facilitar el acceso a convenios, legislación, cálculos laborales y generación de reclamaciones mediante una interfaz moderna y funcionalidades de IA.

## 🏗 Arquitectura
### Frontend
- **Framework**: Next.js 16 (App Router)
- **UI**: React 19, Lucide React, Framer Motion
- **Estructura**: Modular (`src/features/`) alineada con el dominio
- **Componentes Clave**: `CascadingSelector` (Empresa -> Grupo -> Nivel)
- **SEO**: `sitemap.ts` y `robots.ts` configurados (Auto-generados).

### Backend (`/backend`)
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15 + PgVector (Dockerized)
- **AI/RAG**:
    - **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)
    - **LLM**: Google Gemini 2.0 Flash (via API)
    - **Intent Detection**: Logic to classify queries (Salary, Dismissal, Leave) and swap system prompts.
- **Data Foundations**:
    - **Extraction**: `extract_salary_tables.py` (Menzies, Swissport, Iberia, Groundforce).
    - **Seeding**: `seed_salary_tables.py` (Multi-company loop).
- **Services**:
    - `CalculatorService`: Supports manual concept inputs and DB-backed salary data.
    - `RagEngine`: Injects user profile context and uses Kinship Tables (`kinship.py`) to prevent hallucinations.

### DevOps
- **Containerización**: Docker Compose
- **Servicios**: PostgreSQL + PgVector, Backend, Frontend
- **Repositorio**: GitHub (`Ulimz/Asesor-Handling`)
- **Documentación**: Centralizada en `docs/active/`.

## 🚦 Estado Actual: PRE-ROLLOUT (Fase 6 Lista)

| Módulo | Estado Frontend | Estado Backend | Notas |
|--------|-----------------|----------------|-------|
| **Usuarios** | ✅ Perfil Dinámico | ✅ Persistencia | Inyectado en Contexto Chat |
| **Convenios** | ✅ Completo | ✅ Completo | Búsqueda semántica activa |
| **Calculadoras** | ✅ Cascading Selector | ✅ Metadata API | Datos reales BOE (750+ registros) |
| **Alertas** | ✅ Completo | ✅ Completo | Feed de novedades |
| **Reclamaciones** | ✅ Completo | ✅ Completo | Generador de escritos |
| **IA/RAG** | ✅ Context Aware | ✅ Kinship Logic | Rules-based Parentesco check |

## 📦 Fases Completadas (Plan Maestro "No Half Measures")

- ✅ **Fase 1: Data Foundations**: Extracción avanzada y seeding real.
- ✅ **Fase 2: Logic & API**: Metadatos dinámicos.
- ✅ **Fase 3: Dynamic UX**: Selectores en cascada y persistencia.
- ✅ **Fase 4: Advanced Features**: Kinship tables y Context Injection.
- ✅ **Limpieza**: Documentación reorganizada y backup creado.

## 🔧 Últimas Actualizaciones
- **Auditoría**: Verificación de código vs tareas (Todo ok).
- **Cleanup**: Archivos root movidos a `docs/`.
- **Backup**: Zip generado en `backups/`.

## 📋 Tareas Activas (Backlog Inmediato)
1.  **Deploy to Production**: Push final a GitHub.
2.  **Smoke Test**: Verificar en prod que la IA respeta la tabla de parentesco.
