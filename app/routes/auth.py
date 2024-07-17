import sys
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user

from app.utils.forms import LoginForm, RegisterForm, ChangePasswordForm
from app import bcrypt, login_manager
from app.utils.models import AppUser
from app import db

auth = Blueprint('auth', __name__)

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


@login_manager.user_loader
def load_user(user_id):
    return AppUser.query.get(int(user_id))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = AppUser.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect(url_for('main.dashboard'))
        else:
            pass
            # Handle user not found

    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = AppUser(username = form.username.data,
                        first_name = form.first_name.data,
                        last_name = form.last_name.data,
                        email_address = form.email.data,
                        password_hash = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))

    return render_template('register.html', form = form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/change_password', methods=['GET','POST'])
@login_required
def change_password():

    form = ChangePasswordForm()

    if form.validate_on_submit():


        # make new password
        new_password_hash = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')

        current_user.password_hash = new_password_hash
        db.session.commit()

        # Do something
        return None
    
    return render_template('change_password.html', form=form)