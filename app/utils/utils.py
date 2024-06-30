import os
from flask import jsonify
import json
import hmac
import uuid
import sys
import hashlib
import pytz
from datetime import datetime

from app import db
from app.utils.models import Ticket

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


TRANSACTION_SECRET_KEY = os.getenv('TRANSACTION_SECRET_KEY')

def validate_ticket(transaction_hmac):
    ticket = Ticket.query.filter_by(transaction_hmac=transaction_hmac).first()
    if ticket:
        expected_hmac = hmac.new(TRANSACTION_SECRET_KEY.encode(), ticket.transaction_id.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(transaction_hmac, expected_hmac):
            
            return {
                'status' : 'valid',
                'buyer_name' : ticket.buyer_name,
                'seller_name' : ticket.seller_name,
                'concert' : ticket.concert,
                'num_tickets' : ticket.num_tickets,
                'times_used' : ticket.times_used
            }, 200
        
        else:
            return {'status': 'invalid_hmac'}, 403
    else:
        return {'status': 'invalid'}, 404

def create_ticket(seller_name: str,
                  seller_email: str,
                  buyer_name: str,
                  concert: str,
                  num_tickets: int) -> str:

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

    return ticket_url

def claim_ticket(transaction_hmac):

    ticket = Ticket.query.filter_by(transaction_hmac=transaction_hmac).first()

    if not ticket:
        return None

    max_uses = ticket.num_tickets

    if ticket.times_used >= ticket.num_tickets:
        
        overused = True
        return ticket.times_used, max_uses, overused
    else:

        ticket.times_used += 1
        db.session.commit()

        overused = False

        return ticket.times_used, max_uses, overused


def get_concert_time(concert):
    options_file = os.path.join("/flask-app/static/concert_options.json")
    with open(options_file, 'r') as file:
        options = json.load(file)
    
    concerts = options['konserter']

    def find_concert(name):
        for concert in concerts:
            if concert["Namn"] == name:
                return concert
        return None  # Return None if not found

    concert_data = find_concert(concert)
    if concert_data is None:
        return jsonify({'status', 'Concert not found'}), 404
    
    concert_date = concert_data['Datum']
    concert_time = concert_data['Tid']

    concert_datetime = datetime.strptime(f"{concert_date} {concert_time}", r"%Y-%m-%d %H:%M:%S")

    tz = pytz.timezone('Europe/Helsinki')
    concert_datetime = concert_datetime.replace(tzinfo=tz)

    return concert_datetime



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