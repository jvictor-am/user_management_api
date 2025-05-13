#!/bin/bash
set -e

# Create data directory if it doesn't exist
mkdir -p /app/data

# Initialize Alembic if migrations directory doesn't exist
if [ ! -d /app/migrations ]; then
    echo "Initializing Alembic migrations..."
    alembic init migrations
    
    # Need to update the path in env.py to import our models
    sed -i "s/target_metadata = None/from src.domain.models import Base\ntarget_metadata = Base.metadata/" /app/migrations/env.py
fi

# Create a revision if none exists
REVISION_COUNT=$(find /app/migrations/versions -type f -name "*.py" 2>/dev/null | wc -l || echo "0")
if [ "$REVISION_COUNT" -eq "0" ]; then
    echo "Creating initial migration..."
    alembic revision --autogenerate -m "Initial migration"
fi

# Apply migrations
echo "Applying migrations..."
alembic upgrade head

# Start the API server
echo "Starting API server..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
