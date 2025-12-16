# Docker + Google AI Setup

## 🚀 Quick Start

### 1. Configuration (CRITICAL)
This project uses **Google Gemini** for AI features and requires environment variables.

1. **Copy the environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Generate a secure database password**:
   ```bash
   openssl rand -base64 32
   ```

3. **Get your Google API Key**: [Google AI Studio](https://aistudio.google.com/app/apikey)

4. **Update `.env` file** with your values:
   ```bash
   POSTGRES_USER=usuario_prod
   POSTGRES_PASSWORD=<paste_generated_password>
   POSTGRES_DB=asistentehandling
   GOOGLE_API_KEY=AIzaSy...
   ```

**⚠️ IMPORTANT**: Never commit `.env` to Git! It's already in `.gitignore`.

### 2. Start Services
```bash
docker-compose up --build
```

### 3. Initialize Database (First Run Only)
```bash
docker-compose exec backend python scripts/init_db.py
```

## 📦 Services

- **Database**: PostgreSQL + PgVector (Port 5433)
- **Backend**: FastAPI + Google Gemini (Port 8000)
- **Frontend**: Next.js (Port 3000)

## 🧠 AI Capabilities

The system uses a hybrid approach:
1. **Search**: `pgvector` + `sentence-transformers` (Local, Free)
2. **Generation**: `Google Gemini 1.5 Flash` (Cloud, Free Tier)

**Note**: The first time you run the backend, it will download the embedding model (~90MB).

## 🛠️ Development

### Access Services
- Frontend: http://localhost:3002
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Reset Database
```bash
docker-compose down -v
docker-compose up --build
```
