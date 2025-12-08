# 📊 Estado del Proyecto (Asistente_Handling)

Este documento resume el propósito, arquitectura y estado actual del proyecto. Debe revisarse al inicio de cada sesión para mantener el contexto.

## 🎯 Propósito
**Asistente_Handling** es una aplicación legal modular diseñada para trabajadores del sector handling aeroportuario en España. Su objetivo es facilitar el acceso a convenios, legislación, cálculos laborales y generación de reclamaciones mediante una interfaz moderna y funcionalidades de IA.

## 🏗 Arquitectura
### Frontend
- **Framework**: Next.js 16 (App Router)
- **UI**: React 19, Lucide React, Framer Motion
- **Estilos**: Tailwind CSS v4 con Glassmorphism
- **Estructura**: Modular (`src/features/`) alineada con el dominio

### Backend
- **Framework**: FastAPI
- **Base de Datos**: PostgreSQL + PgVector (SQLAlchemy ORM)
- **Búsqueda**: Elasticsearch + PgVector (dual system)
- **IA**: sentence-transformers (local, FREE)
- **Arquitectura**: Services Layer (`legal_engine.py`, `rag_engine.py`)
- **Estructura**: Modular (`backend/app/modules/`)

### DevOps
- **Containerización**: Docker Compose
- **Servicios**: PostgreSQL + PgVector, Backend, Frontend
- **Repositorio**: GitHub (`Ulimz/Asesor-Handling`)

## 🚦 Estado Actual: MVP Completo (Fase 6)

| Módulo | Estado Frontend | Estado Backend | Notas |
|--------|-----------------|----------------|-------|
| **Usuarios** | Pendiente | Estructurado | Auth JWT pendiente |
| **Convenios** | ✅ Completo | ✅ Completo | Búsqueda semántica activa |
| **Calculadoras** | ✅ Completo | ✅ Completo | Nómina con IRPF/SS |
| **Alertas** | ✅ Completo | ✅ Completo | Feed de novedades |
| **Reclamaciones** | ✅ Completo | ✅ Completo | Generador de escritos |
| **IA/RAG** | ✅ Completo | ✅ Completo | Local + PgVector |

## 📦 Fases Completadas

- ✅ **Fase 1-2**: Infraestructura base + Búsqueda semántica
- ✅ **Fase 3**: Calculadora de Nómina (IRPF/SS 2024)
- ✅ **Fase 4**: Sistema de Alertas (Novedades)
- ✅ **Fase 5**: Generador de Reclamaciones
- ✅ **Fase 6**: Docker + PgVector + IA Local (FREE)

## 🔧 Últimas Actualizaciones (2025-12-08)

### Refactorización Services Layer
- Creado `backend/app/services/legal_engine.py` (lógica de nóminas)
- Creado `backend/app/services/rag_engine.py` (búsqueda IA)
- Routers ahora delegan en servicios (mejor testabilidad)

### Infraestructura Docker
- `docker-compose.yml` con 3 servicios
- PostgreSQL + PgVector para búsqueda vectorial
- IA local con `sentence-transformers` (0€ coste)
- Scripts de inicialización (`init_db.py`, `seed_vectors.py`)

## 💡 Próximos Pasos Sugeridos

1. **Testing**: Configurar Vitest/Jest para componentes React
2. **Autenticación**: Implementar JWT para usuarios
3. **Migración de Datos**: Mover datos de Elasticsearch a PgVector
4. **Deployment**: Configurar CI/CD para producción
5. **PDF Export**: Añadir generación de PDFs para reclamaciones
6. **Mobile UI**: Sidebar responsive para dispositivos móviles

## ⚠️ Notas Importantes

- **Dual Search System**: Elasticsearch (legacy) + PgVector (Docker)
- **Primera ejecución Docker**: Descarga modelo IA (~90MB, solo una vez)
- **Coste IA**: 0€ (sentence-transformers local, sin API keys)
- **GitHub**: Todos los cambios guardados en `Ulimz/Asesor-Handling`
