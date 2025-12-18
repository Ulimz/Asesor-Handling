# 📊 Estado del Proyecto (Asistente_Handling)

Este documento resume el propósito, arquitectura y estado actual del proyecto. Debe revisarse al inicio de cada sesión para mantener el contexto.

## 🎯 Propósito
**Asistente_Handling** es una aplicación legal modular diseñada para trabajadores del sector handling aeroportuario en España. Su objetivo es facilitar el acceso a convenios, legislación, cálculos laborales y generación de reclamaciones mediante una interfaz moderna y funcionalidades de IA.

## 🏗 Arquitectura
### Frontend
- **Framework**: Next.js 16 (App Router)
- **UI**: React 19, Lucide React, Framer Motion
- **Estructura**: Modular (`src/features/`) alineada con el dominio
- **Componentes Clave**: 
    - `CascadingSelector`: Selección jerárquica (Empresa -> Grupo -> Nivel).
    - `ProfileSwitcher`: Gestión multi-perfil con soporte móvil.
    - `CompanyDropdown`: Selector optimizado con modo compacto.
- **SEO**: `sitemap.ts` y `robots.ts` configurados.

### Backend (`/backend`)
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15 + PgVector (Railway Production)
- **AI/RAG**:
    - **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)
    - **LLM**: Google Gemini 2.0 Flash (via API)
    - **Hybrid Retrieval**: "Regla de Oro" (Inyección prioritaria de tablas SQL sobre PDF).
- **Data Foundations**:
    - **Canonical Structures 2025**: Aviapartner, Azul Handling, Sector, EasyJet, etc.
    - **Seeding**: `seed_production.py` (Sincronización total DB-Código).

### DevOps
- **Containerización**: Docker Compose
- **Servicios**: PostgreSQL + PgVector, Backend, Frontend
- **Repositorio**: GitHub (`Ulimz/Asesor-Handling`)
- **Documentación**: Centralizada en `docs/active/`.

## 🚦 Estado Actual: PRODUCTION READY (v1.8)

| Módulo | Estado Frontend | Estado Backend | Notas |
|--------|-----------------|----------------|-------|
| **Usuarios** | ✅ Multi-Perfil & Móvil | ✅ Persistencia Relacional | UX mejorada en mobile |
| **Convenios** | ✅ Aviapartner Implantado | ✅ Estructuras 2025 | Datos BOE verídicos |
| **Calculadoras** | ✅ UX Simplificada | ✅ Tablas Salariales SQL | Input "Salario Base" eliminado |
| **Alertas** | ✅ Completo | ✅ Completo | Feed de novedades |
| **Reclamaciones** | ✅ Completo | ✅ Completo | Generador de escritos |
| **IA/RAG** | ✅ Alta Precisión | ✅ Structured Injection | Prioridad absoluta a datos SQL |

## 📦 Hitos Recientes (Completados)

- ✅ **Aviapartner 2025**: Integración total de la estructura salarial y tablas del convenio.
- ✅ **Mobile UX Refinement**: 
    - Header reorganizado (Logo -> Icono -> Perfil -> Menú).
    - Menú simplificado (Acceso a Configuración).
- ✅ **RAG "Regla de Oro"**: El chat responde preguntas de sueldo consultando la base de datos, no alucinando PDFs.
- ✅ **Clean Code**: Eliminación de redundancias en JSONs y inputs innecesarios.

## 🔧 Próximos Pasos (Roadmap)
### Corto Plazo
1. **Empaquetado Mobile**: Capacitor JS (Android/iOS).
2. **Performance**: Cacheo de selectores.
3. **Monitoring**: Dashboards en Railway.

### v2.0 (I+D)
4. **Búsqueda Híbrida**: Integración de Google Search para noticias/actualidad.
5. **Agente Calculadora**: Tool calling para que la IA "opere" nóminas.
6. **Memoria de Usuario**: Recordar contexto histórico.
7. **Modo Voz**: Interfaz conversacional por audio.

## 📋 Tareas Activas
- [ ] Monitorizar estabilidad en producción tras despliegue v1.8.
