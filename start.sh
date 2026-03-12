#!/bin/bash
set -e  # Exit on any error

echo "=== Starting Application Startup ==="
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Database URL: ${DATABASE_URL:0:30}..."

# Check if alembic is available
echo "Checking alembic..."
which alembic || echo "Alembic not found in PATH"
alembic --version || echo "Could not get alembic version"

# List available migrations
echo "Available migrations:"
ls -la alembic/versions/ || echo "No migrations directory found"

# Run database migrations
echo "Running database migrations..."
alembic current
alembic upgrade head
echo "Migrations completed successfully!"

# Check if tables were created
echo "Checking database tables..."
python -c "
from app.config import get_settings
from app.db import engine
from sqlalchemy import inspect
settings = get_settings()
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'Tables in database: {tables}')
" || echo "Could not check tables"

# Start the application
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
