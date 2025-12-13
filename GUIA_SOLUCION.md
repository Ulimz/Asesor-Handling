# Guía de Solución: Despliegue y Datos faltantes

He realizado los cambios en el código para que la aplicación funcione correctamente en la nube. Sin embargo, hay **2 pasos críticos** que debes ejecutar tú en Railway para que los cambios surtan efecto.

## ✅ Cambios ya realizados (Código):
1.  **Arreglado el error de conexión Frontend**: Se ha modificado `src/config/api.ts` para que detecte la variable de entorno `NEXT_PUBLIC_API_URL` en lugar de usar siempre `localhost`.
2.  **Creado script de Datos**: Se ha creado `scripts/seed_prod_data.sh` para cargar los datos en la nube.
3.  **Git Limpio**: Se han añadido los archivos faltantes a un commit y se ha limpiado el repositorio de archivos basura.

---

## 🚀 Pasos que DEBES realizar ahora:

### 1. Subir cambios a GitHub
Abre tu terminal y ejecuta:
```bash
git push origin main
```
*Esto enviará el código corregido a Railway y disparará un nuevo despliegue.*

### 2. Configurar Variable de Entorno en Railway (CRÍTICO)
1.  Entra a tu proyecto en **Railway Dashboard**.
2.  Ve al servicio **Frontend** (Next.js) -> Pestaña **Variables**.
3.  Añade una nueva variable:
    *   **Nombre/Key**: `NEXT_PUBLIC_API_URL`
    *   **Valor**: `https://<TU-URL-BACKEND-RAILWAY>.up.railway.app`
    *(Asegúrate de copiar la URL de tu servicio backend, SIN la barra al final)*.
4.  Railway redeployará automáticamente.

### 3. Cargar los Datos (Poblar la Base de Datos)
La base de datos de producción está vacía. Para llenarla:
1.  En Railway, ve a tu servicio **Backend** -> **CLI/Terminal**.
2.  Ejecuta el script que he creado:
    ```bash
    sh scripts/seed_prod_data.sh
    ```
    *(Si da error de permisos, intenta: `python backend/seed_cloud_db.py`)*

### Resultado Esperado
*   La **Calculadora** mostrará datos porque ya hay convenios en la BD.
*   La **Web** conectará con el backend porque ya tiene la variable de entorno correcta.
