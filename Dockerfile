# ================================
# STAGE 1 — Build React Frontend
# ================================
FROM node:18 AS frontend-builder

WORKDIR /app/frontend

# Copy package.json first
COPY ai_demo_frontend/package*.json ./
RUN npm install

# Copy full frontend source
COPY ai_demo_frontend ./

# Build frontend
RUN npm run build


# ================================
# STAGE 2 — Backend Builder
# ================================
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt


# ================================
# STAGE 3 — Final Image
# ================================
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local

# Copy backend code
COPY . .

# Create frontend folder BEFORE copying build
RUN mkdir -p /app/ai_demo_frontend/dist

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist/ /app/ai_demo_frontend/dist/

RUN adduser --disabled-password appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]