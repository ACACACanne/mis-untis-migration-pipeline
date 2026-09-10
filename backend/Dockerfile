FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal OS dependencies required for lxml, Postgres, and health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cache and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy Alembic migration environment and application source code
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY app/ ./app/

# Expose the FastAPI backend port
EXPOSE 8000

# Run FastAPI using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]