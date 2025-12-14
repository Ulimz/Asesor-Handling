## 📅 Fecha
2025-12-13

## ✅ Qué se hizo hoy
1.  **Calculadora de Nómina (Azul Handling)**:
    *   **Corrección de Datos**: Detectada falta de conceptos "Jornada Fraccionada".
    *   **Implementación**: Añadidos 3 tipos placeholder ("Corta", "Media", "Larga") en `azul.json`.
    *   **Sincronización**: Script `run_seed_cloud_concepts.py` ejecutado para actualizar la BD de Producción.
2.  **Reparación Entorno Local y Nube**:
    *   **Backend Local**: Solucionado crash por falta de dependencias (`fastapi`, `uvicorn`, `argon2-cffi`, `pgvector`).
    *   **Configuración**: Corregido `.env` local que tenía caracteres corruptos en `DATABASE_URL`.
    *   **Backend Producción**: Actualizado `requirements.txt` con `argon2-cffi` para evitar boot loop.
    *   **Chat IA**: Depurado error "Lo siento...". Causa confirmada: Falta de `GOOGLE_API_KEY` en Railway (usuario notificado).

## 📝 Estado Actual
*   **Calculadora**: FUNCIONAL en Producción (datos parcheados, pendientes de validar precios reales).
*   **Chat IA**: FUNCIONAL (si se configura la API KEY).
*   **Despliegue**: Estable en rama `main`.

## ⚠️ Advertencias para Mañana
*   **Precios Reales**: Los pluses de "Fraccionada" tienen nombres genéricos. El usuario debe facilitar los precios exactos para editarlos en `azul.json`.
*   **Variables Nube**: Verificar que `GOOGLE_API_KEY` persiste en Railway tras el redeploy.

## 📋 Lista de Tareas (Próximos Pasos)
- [ ] **Validación Usuario**: Confirmar que los cálculos de nómina coinciden con la realidad.
- [ ] **Refinamiento**: Sustituir placeholders de Fraccionada por nombres/precios reales.
- [ ] **Móvil**: Verificar experiencia de usuario en móvil (punto pendiente anterior).
