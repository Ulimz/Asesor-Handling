# 📋 Lista de Tareas (Asistente Handling)

## 🔴 URGENTE (Prioridad Inmediata)
- [x] **FIX CRÍTICO: "Sin Perfil" Bug**
  - [x] Investigar causa raíz (Next.js Cache en `fetch`)
  - [x] Verificar respuesta de API (Backend ok, devuelve perfiles)
  - [x] Implementar fix: `cache: 'no-store'` en `api-service.ts`
  - [/] Verificar en producción (Requiere redespilegue)

## 🦅 Estructura Canónica EasyJet (2025)
- [x] **Análisis Profundo**: Identificar Jefes A/B/C y Variables en XML/Tablas.
- [x] **Documentación**: Crear `ESTRUCTURA_CANONICA_EASYJET.md`.
- [x] **JSON Template**: `backend/data/structure_templates/easyjet.json` (Flat Structure).
- [x] **Seeding**: Script `seed_easyjet_root.py` ejecutado y verificado en PROD.
- [ ] **Validación UI**: Verificar visualización en Calculadora (Pendiente User).

## 📅 Próximos Pasos (Inmediato)
- [ ] **Deployment**: Push a GitHub para disparar build
- [ ] **Smoke Test**: Verificar que al crear perfil ya no sale "Sin Perfil"
- [x] **Docker**: Corregir warnings de ENV format en Dockerfile

## 🚑 Gestión de Incidencias (Restauración)
- [x] **Restore Concepts**: Recuperados conceptos de TODAS las compañías (Template Source).
- [x] **Correct Slugs**: Migrados slugs (`azul`->`azul-handling`) y propagación a Sector.
- [x] **EasyJet**: Corregida carga de conceptos (Dict vs List).

## 👑 Panel de Administración (Superusuario)
- [x] Actualizar Política de Privacidad (GDPR Admin Access).
- [x] Backend: `admin_router.py` (Users/Stats endpoints).
- [x] Backend: Registrar router en `main.py`.
- [x] Frontend: `src/app/admin/page.tsx` (Dashboard UI).
- [x] Frontend: `Sidebar.tsx` (Link condicional).
- [x] Frontend: `UserContext` (Types update).

## 🛠 Corto Plazo (Completado)
- [x] **Settings Page**: Añadir gestión de perfiles (Editar/Eliminar)
- [x] **Onboarding**: Crear primer perfil durante registro
- [x] **Data Migration**: Script para usuarios legacy (si es necesario)
- [x] **FIX**: Chat funciona con perfil activo.
- [x] **FIX**: Calculadora auto-rellena datos de perfil.

## 🔮 Medio Plazo
- [ ] Profile Presets & Sharing
- [ ] Analytics por perfil
- [ ] Mobile Optimization (ProfileSwitcher)
