"""
Admin Database (MySQL/Laravel Source of Truth)
Handles connections to the primary Laravel database for the AyurEze ecosystem.
"""

import os
import logging
import urllib.parse
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load credentials
load_dotenv()

logger = logging.getLogger(__name__)

class AdminDBManager:
    """Manages the legacy/admin MySQL database connection"""
    
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.engine = None
        self.SessionLocal = None
        
        if self.db_url and self.db_url.startswith("mysql"):
            try:
                # Core Engine Setup
                self.engine = create_engine(
                    self.db_url,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    connect_args={"connect_timeout": 10}
                )
                self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
                logger.info("✅ Admin Backend (MySQL) engine initialized")
            except Exception as e:
                logger.error(f"❌ Admin Backend connection failed: {e}")
        else:
            logger.warning("⚠️ No DATABASE_URL (MySQL) found in environment")

    def is_connected(self) -> bool:
        """Check if MySQL is reachable"""
        if not self.engine: return False
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except:
            return False

    @contextmanager
    def get_session(self):
        """Context manager for SQLAlchemy sessions"""
        if not self.SessionLocal:
            raise RuntimeError("Admin database not initialized")
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

# Global singleton
admin_db = AdminDBManager()

def get_admin_db():
    """Dependency for FastAPI"""
    if not admin_db.SessionLocal:
        return None
    db = admin_db.SessionLocal()
    try:
        yield db
    finally:
        db.close()
