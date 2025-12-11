# Guía de Publicación: Asistente Handling (Todo en Railway)

Esta guía te permitirá desplegar toda la aplicación (Base de Datos + Backend + Frontend) usando **solo Railway** con el plan Hobby.

> [!NOTE]
> Al usar el plan Hobby ($5/mes), puedes tener proyectos privados y recursos suficientes que nunca se "duermen".

## 🏗️ Arquitectura Simplificada
*   **Base de Datos**: PostgreSQL en Railway (con pgvector).
*   **Backend**: Railway (Python/FastAPI).
*   **Frontend**: Railway (Next.js) O Vercel (Opcional, pero Railway lo aguanta todo).
    *   *Recomendación*: Usaremos Vercel para el Frontend (es gratis y más rápido para Next.js) y Railway para Backend + Datos.

---

## Parte 1: Preparar Railway (Backend + Base de Datos)

### 1. Crear Proyecto y Base de Datos
1.  Entra en [railway.app](https://railway.app) y asegúrate de tu plan Hobby.
2.  **+ New Project** -> **Provision PostgreSQL**.
3.  Esto creará una base de datos vacía.
4.  Haz clic en la tarjeta de PostgreSQL -> **Data** -> Pestaña **Variables**.
5.  Copia la `DATABASE_URL` (la que empieza por `postgresql://...`). Esta es **CRÍTICA**.
6.  Activa la extensión vectorial:
    *   Pestaña "Query".
    *   Escribe: `CREATE EXTENSION IF NOT EXISTS vector;`
    *   Ejecutar.

### 2. Desplegar el Backend
1.  En el mismo proyecto de Railway, dale a **+ Create** -> **GitHub Repo**.
2.  Selecciona `Asistente_Handling`.
3.  **Configurar Variables** (Antes de que termine el deploy):
    *   Haz clic en la tarjeta del repo.
    *   Pestaña **Variables**.
    *   Añade:
        *   `DATABASE_URL`: (Pega la que copiaste del paso 1).
        *   `GOOGLE_API_KEY`: (Tu clave de Gemini).
        *   `JWT_SECRET`: (Inventa una contraseña larga).
        *   `ALGORITHM`: `HS256`
        *   `ACCESS_TOKEN_EXPIRE_MINUTES`: `60`
    *   Pestaña **Settings** -> **Root Directory**: Escribe `/backend`.
4.  Railway detectará el `Dockerfile` y empezará a construir.
    *   *Nota*: Tardará unos 3-5 minutos.
5.  Cuando termine y salga "Active", ve a **Settings** -> **Networking** -> **Generate Domain**.
    *   Copia ese dominio (ej: `asistente-production.up.railway.app`). Esta es tu `API_URL`.

---

## Parte 2: Llenar la Base de Datos (Seed)

Ahora que el backend está corriendo en la nube, necesitamos meterle los datos iniciales (Convenios, Usuarios, etc).

1.  En tu **PC Local**:
    *   Crea un archivo `.env.production` (o edita el `.env` temporalmente).
    *   Pon la `DATABASE_URL` de Railway.
2.  Abre una terminal en `/backend`:
    ```powershell
    # Instalar dependencias si faltan
    pip install psycopg2-binary pgvector
    
    # Ejecutar script de carga
    python init_db_resources.py
    ```
3.  Si dice "Éxito", tu base de datos en la nube ya tiene los PDFs y tablas.

---

## Parte 3: Publicar Frontend (Vercel)

Vercel es el "hogar nativo" de Next.js y es gratis para uso personal.

1.  Ve a [vercel.com](https://vercel.com) -> **Add New** -> **Project**.
2.  Importa el repo `Asistente_Handling`.
3.  **Environment Variables**:
    *   `NEXT_PUBLIC_API_URL`: Pega el dominio de tu backend en Railway (Añade `https://` al principio si falta, y `/api` al final si tu backend lo requiere, pero normalmente la raíz vale. Ejemplo: `https://asistente-production.up.railway.app`).
4.  **Deploy**.

---

## 🚀 Verificación
Entra a tu web de Vercel.
1.  Prueba a **Registrarte**.
2.  Prueba el **Chat**.
3.  ¡Listo!
