import os
from flask import jsonify
import json
import hmac
import uuid
import hashlib

from app import app
from app.utils.db import db, Ticket


TRANSACTION_SECRET_KEY = os.getenv('TRANSACTION_SECRET_KEY')

def validate_ticket(transaction_hmac):
    ticket = Ticket.query.filter_by(transaction_hmac=transaction_hmac).first()
    if ticket:
        expected_hmac = hmac.new(TRANSACTION_SECRET_KEY.encode(), ticket.transaction_id.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(transaction_hmac, expected_hmac):
            
            return jsonify({
                'status' : 'valid',
                'buyer_name' : ticket.buyer_name,
                'seller_name' : ticket.seller_name,
                'concert' : ticket.concert,
                'num_tickets' : ticket.num_tickets,
                'ticket_valid' : True,
                'times_used' : ticket.times_used
            }), 200
        
        else:
            return jsonify({'status': 'invalid_hmac'}), 403
    else:
        return jsonify({'status': 'invalid'}), 404



'''
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

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