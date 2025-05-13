from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List

class AuthLogRepository(ABC):
    """Repository interface for authentication logs."""
    
    @abstractmethod
    def add_log(self, user_id: Optional[int], ip_address: Optional[str], 
                success: bool, details: Optional[str] = None) -> None:
        """Add a new authentication log entry."""
        pass

    @abstractmethod
    def get_recent_failed_attempts(self, user_id: Optional[int], 
                                  ip_address: Optional[str], 
                                  minutes: int = 60) -> int:
        """Get count of recent failed attempts for a user or IP."""
        pass
