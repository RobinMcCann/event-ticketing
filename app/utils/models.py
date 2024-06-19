from app import db

class Ticket(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        seller_name = db.Column(db.String(80), nullable=False)
        buyer_name = db.Column(db.String(80), nullable=False)
        concert = db.Column(db.String(80), nullable=False)
        num_tickets = db.Column(db.Integer, nullable=False)
        transaction_id = db.Column(db.String(64), nullable=False)
        transaction_hmac = db.Column(db.String(64), unique=True, nullable=False)
        times_used = db.Column(db.Integer, default=0, nullable=False)