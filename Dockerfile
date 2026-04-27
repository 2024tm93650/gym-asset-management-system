# syntax=docker/dockerfile:1.7
# ---------- Stage 1: builder ----------
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt


# ---------- Stage 2: runtime ----------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Create unprivileged user
RUN groupadd --system aceest && useradd --system --gid aceest --home /app aceest

WORKDIR /app

# Copy installed deps from builder stage
COPY --from=builder /install /usr/local

# Copy application source
COPY ACEest_Fitness.py ./
COPY app/ ./app/

USER aceest

EXPOSE 5000

# Liveness probe used by both Docker and Kubernetes
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; \
      sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5000/health',timeout=2).status==200 else 1)"

# 2 workers is plenty for a demo; tune via env in K8s if needed
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "ACEest_Fitness:app"]
