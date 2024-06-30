from flask import jsonify, Blueprint
import os
import json
import sys

utils = Blueprint('utils', __name__)

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

@utils.route('/dropdown_options', methods=['GET'])
def concert_options():
    options_file = os.path.join("/flask-app/static/concert_options.json")
    with open(options_file, 'r') as file:
        options = json.load(file)
    concerts = [concert['Namn'] for concert in options['konserter']]

    return jsonify({
        "konserter": concerts
    }), 200