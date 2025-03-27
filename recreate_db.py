import os
import logging
from app import app, db
from werkzeug.security import generate_password_hash
from models import Admin, Question, Option, Vote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recreate_database():
    """
    Remove existing database and recreate it with fresh schema.
    Also create an admin user if one doesn't exist.
    """
    with app.app_context():
        logger.info("Dropping all tables...")
        db.drop_all()
        
        logger.info("Creating all tables from new schema...")
        db.create_all()
        
        # Create default admin user if necessary
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            logger.info("Created default admin user (username: admin, password: admin123)")
        
        db.session.commit()
        logger.info("Database recreation completed successfully!")

if __name__ == "__main__":
    # Check if database file exists, and remove it (for SQLite)
    db_path = 'instance/database.db'
    if os.path.exists(db_path):
        logger.info(f"Removing existing database file: {db_path}")
        os.remove(db_path)
    
    # Recreate database
    recreate_database()