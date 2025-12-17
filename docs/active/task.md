# 📋 Lista de Tareas (Asistente Handling)

## 🔴 URGENTE (Prioridad Inmediata)
- [x] **FIX CRÍTICO: "Sin Perfil" Bug**
  - [x] Investigar causa raíz (Next.js Cache en `fetch`)
  - [x] Verificar respuesta de API (Backend ok, devuelve perfiles)
  - [x] Implementar fix: `cache: 'no-store'` en `api-service.ts`
  - [/] Verificar en producción (Requiere redespilegue)

## 📅 Próximos Pasos (Inmediato)
- [ ] **Deployment**: Push a GitHub para disparar build
- [ ] **Smoke Test**: Verificar que al crear perfil ya no sale "Sin Perfil"
- [ ] **Docker**: Corregir warnings de ENV format en Dockerfile

## 🛠 Corto Plazo
- [ ] **Settings Page**: Añadir gestión de perfiles (Editar/Eliminar)
- [ ] **Onboarding**: Crear primer perfil durante registro
- [ ] **Data Migration**: Script para usuarios legacy (si es necesario)

## 🔮 Medio Plazo
- [ ] Profile Presets & Sharing
- [ ] Analytics por perfil
- [ ] Mobile Optimization (ProfileSwitcher)
