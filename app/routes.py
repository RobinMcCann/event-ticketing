import pstats
from flask import (render_template, 
                   request, 
                   jsonify, 
                   Blueprint
                   )
from datetime import datetime
import os
import json
import hmac
import uuid
import hashlib
 
from app.utils.utils import validate_ticket
from app.utils.models import Ticket

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/view_ticket/<transaction_hmac>', methods=['GET'])
def view_ticket(transaction_hmac):

    ticket, status = validate_ticket(transaction_hmac)

    if status == 200:
        valid_status = "Ja" if ticket['ticket_valid'] else "Nej"
        # Render Ticket
        return render_template('view_ticket.html',
                                buyerName = ticket['buyer_name'],
                                sellerName = ticket['seller_name'],
                                concert = ticket['concert'],
                                numTickets = ticket['num_tickets'],
                                ticketValid = valid_status,
                                timesUsed = ticket['times_used'])

    elif status == 403:
        return ticket
    elif status == 404:
        return ticket

@bp.route('/request_ticket', methods=['POST'])
def request_ticket():
    data = request.json
    seller_name = data['seller_name']
    seller_email = data['seller_email']
    buyer_name = data['buyer_name']
    concert = data['concert']
    num_tickets = data['num_tickets']
    transaction_id = str(uuid.uuid4())

    TRANSACTION_SECRET_KEY = os.getenv('TRANSACTION_SECRET_KEY')

    # Generate HMAC for the transaction ID
    transaction_hmac = hmac.new(TRANSACTION_SECRET_KEY.encode(), transaction_id.encode(), hashlib.sha256).hexdigest()
    
    new_ticket = Ticket(seller_name=seller_name,
                        buyer_name=buyer_name,
                        concert=concert,
                        num_tickets=num_tickets,
                        transaction_id=transaction_id,
                        transaction_hmac=transaction_hmac)

    from app import db

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


@bp.route('/dropdown_options', methods=['GET'])
def concert_options():
    options_file = os.path.join("/flask-app/static/concert_options.json")
    with open(options_file, 'r') as file:
        options = json.load(file)
    return jsonify(options)
