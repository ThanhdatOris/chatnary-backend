# Dockerfile for Chatnary Python Backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY run.py .
COPY env.example .

# Create necessary directories
RUN mkdir -p uploads vector_stores logs

# Create non-root user for security
RUN addgroup --system --gid 1001 chatnary && \
    adduser --system --uid 1001 --gid 1001 chatnary

# Change ownership of app directory
RUN chown -R chatnary:chatnary /app

# Switch to non-root user
USER chatnary

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "run.py"]
