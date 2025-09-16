# Dockerfile for Chatnary Python Backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies with SSL support
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ca-certificates \
    openssl \
    libssl-dev \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY run.py .
COPY .env ./

# Create necessary directories
RUN mkdir -p uploads vector_stores logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "run.py"]
