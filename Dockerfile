# Stage 1 - builder
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install dependencies to a target folder
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# Stage 2 - runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only (copy from builder)
COPY --from=builder /install /usr/local
COPY . .

# Use a non-root user (optional security)
RUN adduser --disabled-password appuser && chown -R appuser /app
USER appuser

# Expose port (default FastAPI)
EXPOSE 8000

# Command to run FastAPI (update if using different runner)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]