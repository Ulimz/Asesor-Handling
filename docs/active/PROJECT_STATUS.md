# 📊 Estado del Proyecto (Asistente_Handling)

Este documento resume el propósito, arquitectura y estado actual del proyecto. Debe revisarse al inicio de cada sesión para mantener el contexto.

## 🎯 Propósito
**Asistente_Handling** es una aplicación legal modular diseñada para trabajadores del sector handling aeroportuario en España. Su objetivo es facilitar el acceso a convenios, legislación, cálculos laborales y generación de reclamaciones mediante una interfaz moderna y funcionalidades de IA.

## 🏗 Arquitectura
### Frontend
- **Framework**: Next.js 16 (App Router)
- **UI Data**: React 19, Lucide React, Framer Motion
- **Estilos**: Tailwind CSS v4
- **Estructura**: Modular (`src/features/`) alineada con el dominio.

### Backend
- **Framework**: FastAPI
- **Base de Datos**: PostgreSQL (SQLAlchemy ORM)
- **Búsqueda**: Elasticsearch
- **Estructura**: Modular (`backend/app/modules/`) espejo del frontend.

## 🚦 Fase Actual: Desarrollo de MVP
Nos encontramos en la fase de construcción de funcionalidades core.

| Módulo | Estado Frontend | Estado Backend |
|--------|-----------------|----------------|
| **Usuarios** | En progreso | Estructurado |
| **Convenios** | Estructurado | Estructurado |
| **Calculadoras** | Estructurado | Estructurado |
| **Alertas** | Estructurado | Estructurado |
| **IA** | Estructurado | Estructurado |

## 💡 Sugerencias de Mejora
1. **Testing Frontend**: Configurar Vitest/Jest para pruebas unitarias de componentes React.
2. **Validación de Tipos**: Asegurar congruencia estricta entre modelos Pydantic (Backend) e interfaces TypeScript (Frontend).
3. **CI/CD**: Verificar pipelines de GitHub Actions para linting y testing automático en PRs.
4. **Documentación API**: Mantener sincronizada la colección de Postman o usar la documentación automática de FastAPI para generar clientes frontend.
