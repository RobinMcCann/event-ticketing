from flask import (render_template, 
                   redirect,
                   url_for,
                   request, 
                   jsonify, 
                   Blueprint,
                   )
from datetime import datetime, timedelta
import os
import json
import hmac
import uuid
import hashlib
import sys
import pytz
 
from app.utils.utils import (create_ticket,
                             validate_ticket,
                             claim_ticket,
                             get_concert_time)

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
    return render_template('login.html')

@bp.route('/order_ticket')
def order_ticket():
    return render_template('order_ticket.html')

@bp.route('/view_ticket/<transaction_hmac>', methods=['GET'])
def view_ticket(transaction_hmac):

    ticket, status = validate_ticket(transaction_hmac)

    if status == 403:
        return ticket # TODO: handling
    elif status == 404:
        return ticket # TODO: handling
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

        if ticket['times_used'] >= ticket['num_tickets']:
            # Return Ticket has already been claimed
            ticket_info["is_valid"] = False

        if current_time > concert_time + timedelta(hours=-1) \
            and current_time < concert_time + timedelta(hours=2):

            ticket_info['is_concert'] = True

        # Render Ticket

        # For debug
        ticket_info['is_concert'] = True

        ticket_info['transaction_hmac'] = transaction_hmac

        return render_template('view_ticket.html',
                                **ticket_info)

    return None

@bp.route('/ticket_created')
def ticket_created():
    data=request.json    

@bp.route('/request_ticket', methods=['POST'])
def request_ticket():

    data = request.form
    seller_name = str(data['firstName']) + str(data['lastName'])
    seller_email = str(data['email'])
    buyer_name = str(data['buyerName'])
    concert = str(data['concert-dropdown'])
    num_tickets = int(data['numTickets'])

    try:

        ticket_url, transaction_id = create_ticket(seller_name=seller_name,
                                                seller_email=seller_email,
                                                buyer_name=buyer_name,
                                                concert=concert,
                                                num_tickets=num_tickets)

        return render_template('view_ordered_ticket.html',
                                ticket_url = ticket_url,
                                seller_name = seller_name,
                                buyer_name = buyer_name,
                                concert = concert,
                                num_tickets = num_tickets,
                                transaction_id = transaction_id,
                                succeeded = True)

    except Exception as e:
        logger.debug(e)
        return render_template('view_ordered_ticket.html',
                               succeeded = False)


@bp.route('/dropdown_options', methods=['GET'])
def concert_options():
    options_file = os.path.join("/flask-app/static/concert_options.json")
    with open(options_file, 'r') as file:
        options = json.load(file)
    concerts = [concert['Namn'] for concert in options['konserter']]

    return jsonify({
        "konserter": concerts
    }), 200

@bp.route('/claim_ticket/<transaction_hmac>', methods=['POST'])
def mark_ticket_as_used(transaction_hmac):

    times_used, max_uses, overused = claim_ticket(transaction_hmac)

    if overused:
        return redirect(url_for('view_ticket', transaction_hmac = transaction_hmac))

    # TODO: Return a page
    if times_used is None:

        info, status = "Biljetten hittades inte.", 404
    else:
        info, status =  f"Biljetten har nu använts {times_used}/{max_uses} gånger.", 200

    return render_template('ticket_used.html', info = info, status = status)
