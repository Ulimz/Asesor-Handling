## 📅 Fecha
2025-12-15 (Sesión 2 - Debugging Tarde)

## ✅ Qué se hizo hoy (continuación)
1.  **Debugging Selectores Vacíos**:
    *   Se identificó que el backend apuntaba al frontend (self-reference) causando 404 en `/api`.
    *   Se corrigió `src/lib/salary-service.ts` para usar la URL correcta del backend (`intelligent-vitality...`).
    *   Se verificó que la BBDD en producción tenía los datos correctos (4034 registros).

## ⚠️ Estado Crítico
*   A pesar de los fixes, el sistema presentó inestabilidad ("muchos fallos") según reporte del usuario.
*   **ACCIÓN TOMADA**: 
    *   Guardado el progreso de debugging en rama `wip-monday-fixes`.
    *   **RESTAURADO BACKUP DE SEGURIDAD** (`backup_20251215_132306`) a la rama `main` para asegurar estabilidad operativa hasta la próxima sesión.

## � Lista de Tareas (Próximos Pasos)
- [ ] Retomar desde `wip-monday-fixes` y verificar si el cambio de URL soluciona definitivamente el problema sin efectos secundarios.
- [ ] Validar integridad de los datos en DB tras el restore.
