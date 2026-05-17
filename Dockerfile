# =============================================================================
#  CreamShop — Dockerfile
#  Multi-stage build: builder installs deps, final image is lean
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1 — Builder: install Python dependencies
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies needed to build psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2 — Final: lean production image
# ---------------------------------------------------------------------------
FROM python:3.12-slim

WORKDIR /app

# Recommended runtime environment defaults
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=CreamShop.settings.prod

# Keep final image lean: update apt lists but do not install build deps here
# Build-time dependencies (gcc, libpq-dev) are installed in the builder stage
RUN apt-get update && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy project source code
COPY . .

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media

# Entrypoint will run migrations/collectstatic at container start (safer than during build)
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create a non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
RUN chown -R appuser:appgroup /app /app/staticfiles /app/media
USER appuser

# Expose port 8000 (Gunicorn will run here)
EXPOSE 8000

# Healthcheck (uses Python stdlib so no extra package required)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; u=urllib.request.urlopen('http://127.0.0.1:8000/'); sys.exit(0 if u.getcode()==200 else 1)"

ENTRYPOINT ["/app/entrypoint.sh"]

# Start Gunicorn
CMD ["gunicorn", "CreamShop.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]