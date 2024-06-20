import pstats
from flask import (render_template, 
                   request, 
                   jsonify, 
                   Blueprint
                   )
from datetime import datetime, timedelta
import os
import json
import hmac
import uuid
import hashlib
import sys
import pytz
 
from app.utils.utils import (validate_ticket,
                             get_concert_time
                             )
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

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/view_ticket/<transaction_hmac>', methods=['GET'])
def view_ticket(transaction_hmac):

    ticket, status = validate_ticket(transaction_hmac)

    if status == 403:
        return ticket
    elif status == 404:
        return ticket
    elif status == 200:

        concert = ticket['concert']
        concert_time = get_concert_time(concert)

        current_time = datetime.now(tz=pytz.utc)
        # Convert current time to same timezone as concert time
        current_time = current_time.astimezone(concert_time.tzinfo)

        ticket_info = ticket
        ticket_info.update({
            "is_valid" : True, # Placeholder, can turn True
            "is_concert" : False # Placeholder, can turn True
        })

        if ticket['times_used'] >= 1:
            # Return Ticket has already been claimed
            ticket_info["is_valid"] = False

        if current_time > concert_time + timedelta(hours=-1) \
            and current_time < concert_time + timedelta(hours=2):

            ticket_info['is_concert'] = True

        # Render Ticket

        # For debugging
        ticket_info['is_concert'] = True

        logger.debug(ticket_info)

        return render_template('view_ticket.html',
                                **ticket_info)

    return None

    

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
    concerts = [concert['Namn'] for concert in options['konserter']]

    return jsonify({
        "konserter": concerts
    }), 200

