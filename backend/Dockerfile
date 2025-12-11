# Dockerfile para Asistente_Handling Backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# Install CPU-only PyTorch (Critical for Railway size limit)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
