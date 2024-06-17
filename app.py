from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import io
import os
import json
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import uuid
import hashlib
import hmac
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'
db = SQLAlchemy(app)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_name = db.Column(db.String(80), nullable=False)
    buyer_name = db.Column(db.String(80), nullable=False)
    concert = db.Column(db.String(80), nullable=False)
    num_tickets = db.Column(db.Integer, nullable=False)
    transaction_id = db.Column(db.Integer, nullable=False)
    transaction_hmac = db.Column(db.String(64), unique=True, nullable=False)
    times_used = db.Column(db.Integer, default=0)

db.create_all()

TRANSACTION_SECRET_KEY = 'your_secret_key'  # Replace with your actual secret key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dropdown_options', methods=['GET'])
def concert_options():
    options_file = os.path.join(app.root_path, 'concert_options.json')
    with open(options_file, 'r') as file:
        options = json.load(file)
    return jsonify(options)

@app.route('/request_ticket', methods=['POST'])
def request_ticket():
    data = request.json
    seller_name = data['seller_name']
    seller_email = data['seller_email']
    buyer_name = data['buyer_name']
    concert = data['concert']
    num_tickets = data['num_tickets']
    transaction_id = str(uuid.uuid4())

    # Generate HMAC for the transaction ID
    transaction_hmac = hmac.new(TRANSACTION_SECRET_KEY.encode(), transaction_id.encode(), hashlib.sha256).hexdigest()
    
    new_ticket = Ticket(seller_name=seller_name,
                        buyer_name=buyer_name,
                        concert=concert,
                        num_tickets=num_tickets,
                        transaction_id=transaction_id,
                        transaction_hmac=transaction_hmac)

    db.session.add(new_ticket)
    db.session.commit()

    # Generate URL with the HMAC
    ticket_url = f"http://localhost:5000/view_ticket/{transaction_hmac}"
    
    # Return ticket details and link
    print(ticket_url)

    return jsonify({
        'transaction_id': transaction_id, 
        'seller_name': seller_name, 
        'buyer_name' : buyer_name,
        'concert' : concert,
        'num_tickets': num_tickets, 
        'ticket_url': ticket_url
        }), 201
        
'''
def send_email(to_email, qr_image, transaction_id):
    msg = MIMEMultipart()
    msg['Subject'] = 'Your Event Ticket'
    msg['From'] = 'your_email@example.com'
    msg['To'] = to_email
    
    img = MIMEImage(qr_image.read())
    img.add_header('Content-ID', '<qr_code>')
    msg.attach(img)
    
    with smtplib.SMTP('smtp.example.com') as server:
        server.login('your_email@example.com', 'password')
        server.sendmail('your_email@example.com', to_email, msg.as_string())
'''

@app.route('/claim_ticket/<transaction_hmac>', methods=['POST'])
def claim_ticket(transaction_hmac):
    pass

@app.route('/view_ticket/<transaction_hmac>', methods=['GET'])
def validate_ticket(transaction_hmac):
    ticket = Ticket.query.filter_by(transaction_hmac=transaction_hmac).first()
    if ticket:
        expected_hmac = hmac.new(TRANSACTION_SECRET_KEY.encode(), ticket.transaction_id.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(transaction_hmac, expected_hmac):
            
            # Render Ticket
            return render_template('view_ticket.html',
                                   buyerName = ticket.buyer_name,
                                   sellerName = ticket.seller_name,
                                   concert = ticket.concert,
                                   numTickets = ticket.num_tickets,
                                   ticketValid = True,
                                   timesUsed = ticket.times_used)
        
        else:
            return jsonify({'status': 'invalid_hmac'}), 403
    else:
        return jsonify({'status': 'invalid'}), 404

if __name__ == '__main__':
    app.run(debug=True)
