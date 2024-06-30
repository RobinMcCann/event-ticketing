from app import db
from flask_login import UserMixin

class Ticket(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        seller_name = db.Column(db.String(80), nullable=False) # TODO: remove
        buyer_name = db.Column(db.String(80), nullable=False)
        concert = db.Column(db.String(80), nullable=False)
        num_tickets = db.Column(db.Integer, nullable=False)
        transaction_id = db.Column(db.String(255), nullable=False)
        transaction_hmac = db.Column(db.String(255), unique=True, nullable=False)
        times_used = db.Column(db.Integer, default=0, nullable=False)
        user_id = db.Column(db.Integer(), db.ForeignKey('app_user.id'))

class AppUser(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key = True)
        username = db.Column(db.String(20), unique=True, nullable=False)
        first_name = db.Column(db.String(80), nullable=False)
        last_name = db.Column(db.String(80), nullable=False)
        email_address = db.Column(db.String(255), nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        tickets = db.relationship('Ticket', backref='user')
