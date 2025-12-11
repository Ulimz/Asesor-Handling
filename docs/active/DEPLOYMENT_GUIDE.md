# Guía de Publicación: Asistente Handling (Nube)

Esta guía te permitirá tener tu web online 24/7 sin dejar tu PC encendido. Usaremos servicios que tienen planes gratuitos o muy baratos.

## 🏗️ Arquitectura
*   **Base de Datos**: **Supabase** (Postgres + pgvector). Gratis y potente.
*   **Backend (Cerebro)**: **Railway** (Python/FastAPI). Muy fácil de configurar.
*   **Frontend (Web)**: **Vercel** (Next.js). El estándar para Next.js.

---

## Paso 1: Base de Datos en la Nube (Supabase)
1.  Entra en [supabase.com](https://supabase.com) y regístrate (es gratis).
2.  Dale a "New Project" y ponle nombre (ej. `produccion-handling`).
3.  **IMPORTANTE**: Copia la contraseña que pongas, no se vuelve a ver.
4.  Cuando se cree (tarda 1 min), ve a **Project Settings -> Database**.
5.  Copia la "Connection String" (Opción URI es mejor). Pégala en un bloc de notas. Será tu `DATABASE_URL`.
6.  Ve al apartado **SQL Editor** (barra lateral izquierda) y dale a "New Query".
7.  Escribe esto para activar vectores: `CREATE EXTENSION IF NOT EXISTS vector;` y dale a **Run**.
8.  Ahora tienes una BD vacía lista.
    *   *Nota: Necesitaremos ejecutar tus scripts de creación de tablas (`init_db_resources.py`) contra esta nueva BD más adelante.*

---

## Paso 2: Subir Código a GitHub
Asegúrate de que todo está subido (ya lo hicimos antes).
1.  Ve a tu repositorio en GitHub para confirmar que ves las carpetas `src` y `backend`.

---

## Paso 3: Publicar el Backend (Railway)
Railway detectará el `Dockerfile` en la carpeta `backend`.
1.  Entra en [railway.app](https://railway.app) y loguéate con GitHub.
2.  Dale a **+ New Project** -> **Deploy from GitHub repo**.
3.  Selecciona tu repo `Asistente_Handling`.
4.  Le das a "Variables" y añades estas (Las tienes en tu `.env` local):
    *   `DATABASE_URL`: Pegas la de Supabase que guardaste.
    *   `GOOGLE_API_KEY`: Tu clave de Gemini.
    *   `SECRET_KEY`: Inventa una larga y segura para el login.
    *   `ALGORITHM`: `HS256`
    *   `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
5.  **Configuración de Root**: Railway te preguntará "¿Dónde está el Dockerfile/Root Directory?". Tienes que decirle que use la carpeta `/backend`.
    *   Settings -> General -> Root Directory: `/backend`
6.  Railway empezará a construir. Si sale bien, te dará una URL pública (ej. `asistente-backend.railway.app`). **Cópiala**.

---

## Paso 4: Inicializar la Base de Datos
Como la BD de Supabase está vacía, tu backend no funcionará al principio.
Desde tu PC local, vamos a "llenar" la BD de la nube una sola vez.
1.  Edita tu archivo `.env` **localmente** (temporalmente) y pon la `DATABASE_URL` de Supabase.
2.  Ejecuta desde terminal:
    ```bash
    cd backend
    python init_db_resources.py
    ```
    *(Asegúrate de tener el entorno virtual activo)*.
3.  Esto creará las tablas en Supabase.
4.  Luego vuelve a poner tu `DATABASE_URL` local en el `.env` para seguir desarrollando en tu PC.

---

## Paso 5: Publicar el Frontend (Vercel)
1.  Entra en [vercel.com](https://vercel.com) y loguéate con GitHub.
2.  **Add New... -> Project** -> Importa tu repo `Asistente_Handling`.
3.  **Framework Preset**: Next.js (lo detecta solo).
4.  **Root Directory**: `./` (la raíz, correcto).
5.  **Environment Variables**:
    *   `NEXT_PUBLIC_API_URL`: Aquí pegas la URL de Railway (ej. `https://asistente-backend.railway.app`). **No pongas `/api` al final si tu código ya lo añade, o ajusta según necesites**. Por defecto tu frontend espera la raíz.
6.  Dale a **Deploy**.

---

## ✅ Resultado Final
Tendrás un dominio de Vercel (ej. `asistente-handling.vercel.app`) que apunta a tu backend en Railway, el cual lee de Supabase.

¡Suerte! Si te atascas en algún paso, dímelo.
