# ============================
# STAGE 1 — Python + Node Builder
# ============================
FROM python:3.11-slim AS builder

# Install OS deps + Node.js (for building the React frontend)
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Work directory
WORKDIR /app

# Copy Python deps first
COPY requirements.txt .

# Install Python deps into /install
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# --- Build React AI Demo ---
COPY ai_demo_frontend ./ai_demo_frontend
RUN cd ai_demo_frontend && npm install && npm run build

# ============================
# STAGE 2 — Runtime Image
# ============================
FROM python:3.11-slim

WORKDIR /app

# Copy installed Python dependencies
COPY --from=builder /install /usr/local

# Copy entire project (including the built dist/ folder)
COPY . .

# For safety, ensure ownership
RUN adduser --disabled-password appuser && chown -R appuser /app
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Launch backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]