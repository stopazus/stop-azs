FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements/base.txt /app/requirements/base.txt
RUN pip install --no-cache-dir -r requirements/base.txt

# Copy application code
COPY api/ /app/api/
COPY sar_parser/ /app/sar_parser/
COPY migrations/ /app/migrations/
COPY alembic.ini /app/alembic.ini

# Expose port
EXPOSE 8000

# Run migrations and start application
CMD ["sh", "-c", "alembic upgrade head && uvicorn api.main:app --host 0.0.0.0 --port 8000"]
