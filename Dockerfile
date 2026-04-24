# Multi-stage Docker build for FalconsScan AI
# Combines React frontend and FastAPI backend in one container

# ============ Stage 1: Build Frontend ============
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY SICKLE-CELL-UI/sickle-cell-ui/package.json ./package.json
COPY SICKLE-CELL-UI/sickle-cell-ui/package-lock.json ./package-lock.json

# Install dependencies
RUN npm ci

# Copy source
COPY SICKLE-CELL-UI/sickle-cell-ui/public ./public
COPY SICKLE-CELL-UI/sickle-cell-ui/src ./src

# Build optimized production bundle
RUN npm run build

# ============ Stage 2: Runtime with Python Backend ============
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn

# Copy Python backend code
COPY app/ ./app/
COPY models/ ./models/
COPY inference.py .

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/build ./frontend_build

# Create startup script
RUN echo '#!/bin/bash\n\
export PORT=${PORT:-8000}\n\
echo "Starting FalconsScan AI on port ${PORT}"\n\
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}\n' > /app/start.sh && chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\", \"8000\")}/health')" || exit 1

# Expose port
EXPOSE 8000

# Run startup script
CMD ["/app/start.sh"]
