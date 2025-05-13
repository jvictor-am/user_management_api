from datetime import datetime, timedelta, timezone
from typing import Optional, List
from sqlalchemy.orm import Session

from src.domain.repositories.auth_log_repository import AuthLogRepository
from src.infrastructure.database.models.auth_log_model import AuthLogModel

class SQLiteAuthLogRepository(AuthLogRepository):
    def __init__(self, db: Session):
        self.db = db

    def add_log(self, user_id: Optional[int], ip_address: Optional[str], 
                success: bool, details: Optional[str] = None) -> None:
        """Add a new authentication log entry."""
        auth_log = AuthLogModel(
            user_id=user_id,
            ip_address=ip_address,
            success=success,
            details=details
        )
        self.db.add(auth_log)
        self.db.commit()

    def get_recent_failed_attempts(self, user_id: Optional[int], 
                                  ip_address: Optional[str], 
                                  minutes: int = 60) -> int:
        """Get count of recent failed attempts for a user or IP."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        query = self.db.query(AuthLogModel).filter(
            AuthLogModel.success == False,
            AuthLogModel.timestamp >= cutoff_time
        )
        
        if user_id:
            query = query.filter(AuthLogModel.user_id == user_id)
        elif ip_address:
            query = query.filter(AuthLogModel.ip_address == ip_address)
        else:
            return 0
            
        return query.count()
