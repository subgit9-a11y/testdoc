
import logging
from app.database_models import engine, Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Creating database tables...")
    try:
        # Create all tables defined in the Base metadata
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables created successfully!")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    init_db()
