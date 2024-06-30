from flask_sqlalchemy import SQLAlchemy
import os
import time
import sqlalchemy

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db
from app.utils.models import Ticket, AppUser

# Set up logging
import logging
# Configure the root logger
logging.basicConfig(
    level=logging.DEBUG,  # Adjust the level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Ensure logs are written to stdout
    ]
)

logger = logging.getLogger(__name__)


# Define the lock file path
LOCK_FILE = "/flask-app/.db_init_lock"

def utilize_db_lock(func):

    def wrapper():

        # Try to acquire the lock
        while os.path.exists(LOCK_FILE):
            time.sleep(1)  # Wait if lock file exists
        open(LOCK_FILE, 'w').close()

        try:
            func()
        except Exception as e:
            logger.debug(e)

        # Release the lock
        os.remove(LOCK_FILE)
    
    return wrapper


@utilize_db_lock
def initialize_db():
    logger.debug("SSS")
    logger.info("Initializing database.")
    app = create_app()
    # Your database initialization logic here
    with app.app_context():
        engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        inspector = sqlalchemy.inspect(engine)

        logger.debug("Something")

        # Check if any table in the metadata is missing
        all_tables_exist = all(table_name in inspector.get_table_names() for table_name in db.metadata.tables.keys())
        
        if not all_tables_exist:
            db.create_all()

        logger.debug("Something2")
    
    logger.info("Database initialized.")


# For ensuring that connection to db is working before doing anything else
def wait_for_db():
    app = create_app()
    with app.app_context():
        retries = 5
        while retries > 0:
            try:
                logger.info("Trying to connect to the database...")
                # Attempt to connect to the database
                db.engine.execute("SELECT 1")
                logger.info("Database connection successful!")
                return
            except Exception as e:
                retries -= 1
                logger.error("Database connection failed. Retrying in 5 seconds...")
                print(e)
                time.sleep(5)
        logger.error("Could not connect to the database after several attempts.")
        sys.exit(1)

if __name__ == '__main__':
    wait_for_db()

    initialize_db()

