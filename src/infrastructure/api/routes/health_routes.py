import os
import time
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.infrastructure.database.database import get_db

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

start_time = time.time()

@router.get("/")
async def health_check():
    """Basic health check."""
    return {
        "status": "ok",
        "uptime": time.time() - start_time
    }

@router.get("/readiness")
async def readiness_check(db: Session = Depends(get_db)):
    """Database readiness check."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok" if db_status == "ok" else "error",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/info")
async def system_info():
    """System information."""
    return {
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "python_version": os.getenv("PYTHON_VERSION", "3.11"),
        "hostname": os.getenv("HOSTNAME", "localhost")
    }
