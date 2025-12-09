# Docker + Google AI Setup

## 🚀 Quick Start

### 1. Configuration (CRITICAL)
This project now uses **Google Gemini** for AI features. You need a free API Key.

1. Get a key: [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create/Update `.env` in `backend/`:
   ```bash
   GOOGLE_API_KEY=AIzaSy...
   ```

### 2. Start Services
```bash
docker-compose up --build
```

### 3. Initialize Database (First Run Only)
```bash
docker-compose exec backend python scripts/init_db.py
```

## 📦 Services

- **Database**: PostgreSQL + PgVector (Port 5432)
- **Backend**: FastAPI + Google Gemini (Port 8000)
- **Frontend**: Next.js (Port 3000)

## 🧠 AI Capabilities

The system uses a hybrid approach:
1. **Search**: `pgvector` + `sentence-transformers` (Local, Free)
2. **Generation**: `Google Gemini 1.5 Flash` (Cloud, Free Tier)

**Note**: The first time you run the backend, it will download the embedding model (~90MB).

## 🛠️ Development

### Access Services
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Reset Database
```bash
docker-compose down -v
docker-compose up --build
```
