from multiprocessing import AuthenticationError
from flask_sqlalchemy import SQLAlchemy
import os
import time
import sqlalchemy

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db, bcrypt
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
    logger.info("Initializing database.")
    app = create_app()
    # Your database initialization logic here
    with app.app_context():
        engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        inspector = sqlalchemy.inspect(engine)

        # Check if any table in the metadata is missing
        all_tables_exist = all(table_name in inspector.get_table_names() for table_name in db.metadata.tables.keys())
        
        if not all_tables_exist:
            db.create_all()

        # Check if admin user exists. If not, create it.
        try_create_admin_user()
    
    logger.info("Database initialized.")


def try_create_admin_user():

    admin_username = os.getenv("APP_ADMIN_UNAME")

    admin = AppUser.query.filter_by(username=admin_username).first()

    if admin:
        if not admin.is_admin:
            raise AuthenticationError("Admin user exists but does not have admin privileges!")
        logger.debug("Admin user already exists.")

    else:
        admin_password = os.getenv("APP_ADMIN_PWORD")
        admin_email_address = os.getenv("APP_ADMIN_EMAIL")
        hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')

        admin_user = AppUser(username = admin_username,
                            first_name = "Admin",
                            last_name = "User",
                            email_address = admin_email_address,
                            password_hash = hashed_password,
                            is_admin = True)
        
        db.session.add(admin_user)
        db.session.commit()

        logger.info("Admin user created.")


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

