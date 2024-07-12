from crypt import methods
from flask import (render_template, 
                   redirect,
                   url_for,
                   request, 
                   Blueprint,
                   )
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import sys
import pytz
import os
 
from app.utils.utils import (create_ticket,
                             validate_ticket,
                             claim_ticket,
                             get_concert_time)

from app.utils.models import Ticket

from app.utils.forms import TicketForm, ClaimTicketForm
from app import login_manager

tickets = Blueprint('tickets', __name__)

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

MAX_TICKETS_PER_ORDER = os.getenv('MAX_TICKETS_PER_ORDER')

@tickets.route('/order_ticket', methods=['GET', 'POST'])
@login_required
def order_ticket():

    form = TicketForm()

    if form.validate_on_submit():
        buyer_name = form.buyername.data
        concert = form.concert.data
        num_tickets = form.number_of_tickets.data

        try:

            ticket_url, transaction_id = create_ticket(buyer_name=buyer_name,
                                                       concert=concert,
                                                       num_tickets=num_tickets)

            seller_name = str(current_user.first_name) + "" + str(current_user.last_name)

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
            render_template('view_ordered_ticket.html',
                            succeeded=False)

    return render_template('order_ticket.html', form=form, max_tickets = MAX_TICKETS_PER_ORDER)

@tickets.route('/view_ticket/<transaction_hmac>', methods=['GET', 'POST'])
def view_ticket(transaction_hmac):

    claim_ticket = ClaimTicketForm()

    if claim_ticket.validate_on_submit():
        return redirect(url_for('tickets.mark_ticket_as_used', transaction_hmac=transaction_hmac))


    ticket, status = validate_ticket(transaction_hmac)

    if status == 403:
        return ticket # TODO: handling
    elif status == 404:
        return ticket # TODO: handling
    elif status == 200:

        concert = ticket['concert']
        concert_time = get_concert_time(concert)
        
        if concert_time is None:
            # TODO: handling
            pass

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
        if os.getenv("DEBUG"):
            ticket_info['is_concert'] = True

        ticket_info['transaction_hmac'] = transaction_hmac

        ticket_info['form'] = claim_ticket

        return render_template('view_ticket.html',
                                **ticket_info)

    return None

@tickets.route('/claim_ticket/<transaction_hmac>', methods=['GET', 'POST'])
def mark_ticket_as_used(transaction_hmac):

    times_used, max_uses, overused = claim_ticket(transaction_hmac)

    if overused:
        return redirect(url_for('tickets.view_ticket', transaction_hmac = transaction_hmac))

    # TODO: Return a page
    if times_used is None:

        info, status = "Biljetten hittades inte.", 404
    else:
        info, status =  f"Biljetten har nu använts {times_used}/{max_uses} gånger.", 200

    return render_template('ticket_used.html', info = info, status = status)


@tickets.route('/view_user_tickets', methods=['GET', 'POST'])
@login_required
def view_user_tickets():
    
    # Here also make admin see and able to manage all tickets

    tickets = Ticket.query.filter_by(user_id = current_user.id)

    return render_template("view_all_tickets.html", user=current_user, tickets=tickets)