# ================================
# STAGE 1 — Build React Frontend
# ================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package.json first
COPY ai_demo_frontend/package*.json ./
# Clean install for better caching
RUN npm ci

# Copy full frontend source
COPY ai_demo_frontend ./

# Build frontend
RUN npm run build


# ================================
# STAGE 2 — Backend Builder
# ================================
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt


# ================================
# STAGE 3 — Final Image
# ================================
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed Python packages
COPY --from=builder /install /usr/local

# Copy backend code
COPY app/ ./app/
COPY main.py .
COPY requirements.txt .
COPY migrations/ ./migrations/

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist/ ./ai_demo_frontend/dist/

# Create user and set permissions
RUN adduser --disabled-password appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]