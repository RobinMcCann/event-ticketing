from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
import sys

main = Blueprint('main', __name__)


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



# TODO: make dashboard.  If user is logged in, '/' redirects to dashboard -> view tickets, order more.
# If user is not logged in, '/' redirects to '/login'


@main.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')