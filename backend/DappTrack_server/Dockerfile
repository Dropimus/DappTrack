# syntax=docker/dockerfile:1.4

## Stage 1: Builder
FROM python:3.11-slim AS builder

# Ensure unbuffered output and resilient pip behavior
ENV PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_RETRIES=5

WORKDIR /app

# Install only build dependencies and clean cache, using BuildKit cache mounts
RUN --mount=type=cache,target=/var/lib/apt/lists \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      gcc \
      libffi-dev \
      libssl-dev \
      build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies into a dedicated prefix, caching pip packages
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


## Stage 2: Runtime
FROM python:3.11-slim

# Keep logs unbuffered
ENV PYTHONUNBUFFERED=1

# Create a non-root user for security
RUN addgroup --system appgroup \
 && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy installed packages and application code
COPY --from=builder /install /usr/local
COPY . ./

# Adjust ownership and switch to non-root user
RUN chown -R appuser:appgroup /app
USER appuser

# Expose FastAPI default port
EXPOSE 8000

# Optional: healthcheck endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
