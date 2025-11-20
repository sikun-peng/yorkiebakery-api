# ================================
# STAGE 1 — Build React Frontend
# ================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY ai_demo_frontend/package*.json ./
RUN npm ci

COPY ai_demo_frontend ./
RUN npm run build


# ================================
# STAGE 2 — Backend Builder (for deps)
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
# STAGE 3 — Test Builder (runs pytest)
# ================================
FROM python:3.11-slim AS testbuilder

RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ⭐ Make Python see the /app folder
ENV PYTHONPATH="/app"
ENV DATABASE_URL="postgresql://fake:fake@localhost:5432/fake"
ENV OPENAI_API_KEY="fake"

COPY --from=builder /install /usr/local
COPY app/ ./app/
COPY main.py .
COPY tests/ ./tests/

RUN pip install pytest

RUN pytest tests/test_imports.py --maxfail=1 --disable-warnings
RUN python -m py_compile $(find app -name "*.py")


# ================================
# STAGE 4 — Final Runtime Image
# ================================
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ⭐ FORCE TESTBUILDER STAGE TO RUN (OPTION 2)
COPY --from=testbuilder /app /tmp/teststage-output

# Copy installed dependencies
COPY --from=builder /install /usr/local

# Copy backend
COPY app/ ./app/
COPY main.py .
COPY requirements.txt .
COPY migrations/ ./migrations/

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist/ ./ai_demo_frontend/dist/

# Create non-root user
RUN adduser --disabled-password appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]