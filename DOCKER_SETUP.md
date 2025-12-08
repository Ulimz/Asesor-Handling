# Docker + PgVector Setup

## 🚀 Quick Start

### 1. Start Services
```bash
docker-compose up --build
```

### 2. Initialize Database
```bash
docker-compose exec backend python scripts/init_db.py
```

### 3. Seed Data (Optional)
```bash
docker-compose exec backend python scripts/seed_vectors.py
```

## 📦 Services

- **Database**: PostgreSQL + PgVector (Port 5432)
- **Backend**: FastAPI (Port 8000)
- **Frontend**: Next.js (Port 3000)

## 🔍 Vector Search

The system uses **sentence-transformers** (100% FREE) for semantic search:
- Model: `all-MiniLM-L6-v2`
- Dimensions: 384
- No API keys needed
- Runs locally

## 🛠️ Development

### Access Services
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Stop Services
```bash
docker-compose down
```

### Reset Database
```bash
docker-compose down -v  # Removes volumes
docker-compose up --build
```
