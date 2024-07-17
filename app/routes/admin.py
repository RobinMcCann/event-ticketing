import sys
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required,current_user

from app import bcrypt, login_manager
from app.utils.models import AppUser
from app import db

admin = Blueprint('admin', __name__)

login_manager.login_view = 'login'

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


@login_required
@admin.route("/user_admin", methods=['GET', 'POST'])
def user_admin():

    if not current_user.is_admin:
        return "NOT AUTHORIZED"

    return "THIS IS THE USER ADMIN PAGE"

@login_required
@admin.route("/ticket_admin", methods=['GET', 'POST'])
def ticket_admin():

    if not current_user.is_admin:
        return "NOT AUTHORIZED"

    return "THIS IS THE TICKET ADMIN PAGE"

