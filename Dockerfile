# BASE: Python 3.9 Slim (Debian-based) for minimal attack surface
FROM python:3.9-slim as builder

# SECURITY: Prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# DEPENDENCIES: Install build dependencies if needed, then python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- FINAL STAGE ---
FROM python:3.9-slim

WORKDIR /app

# SECURITY: Create a non-root user 'aegis'
RUN useradd -m -r -u 1000 -g users aegis

# COPY: Only copy necessary artifacts from builder and source
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy Application Code
# Assuming all python files (server.py, aegis_core.py, etc.) are in the build context root
COPY . .

# SECURITY: Chown application files to non-root user
RUN chown -R aegis:users /app

# SECURITY: Switch to non-root user
USER aegis

# EXPOSE: Port 8000 for the FastAPI server
EXPOSE 8000

# HEALTHCHECK: Simple curl to verify the service is up (assuming a health endpoint exists or root returns 404/200)
# In high-assurance, we might use a specific /health route defined in server.py
# For now, we rely on the orchestrator.

# RUN: Start Uvicorn with production settings
# Workers should be tuned based on CPU cores. Here we use 1 for the demo.
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info"]
