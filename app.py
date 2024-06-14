from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import qrcode
import io
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
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    num_tickets = db.Column(db.Integer, nullable=False)
    transaction_id = db.Column(db.String(120), unique=True, nullable=False)
    transaction_hmac = db.Column(db.String(64), unique=True, nullable=False)
    scanned = db.Column(db.Boolean, default=False)

db.create_all()

SECRET_KEY = 'your_secret_key'  # Replace with your actual secret key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/request_ticket', methods=['POST'])
def request_ticket():
    data = request.json
    name = data['name']
    email = data['email']
    num_tickets = data['num_tickets']
    transaction_id = str(uuid.uuid4())

    # Generate HMAC for the transaction ID
    transaction_hmac = hmac.new(SECRET_KEY.encode(), transaction_id.encode(), hashlib.sha256).hexdigest()
    
    new_ticket = Ticket(name=name, email=email, num_tickets=num_tickets, transaction_id=transaction_id, transaction_hmac=transaction_hmac)
    db.session.add(new_ticket)
    db.session.commit()

    # Generate URL with the HMAC
    validation_url = f"http://localhost:5000/validate_ticket/{transaction_hmac}"
    
    # Generate QR Code with the URL
    qr = qrcode.QRCode()
    qr.add_data(validation_url)
    img = qr.make_image(fill='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)

    qr_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    # Send QR code via email
    #send_email(email, buf, transaction_id)
    
    # Return QR code and details
    return jsonify({
        'transaction_id': transaction_id, 
        'name': name, 
        'num_tickets': num_tickets, 
        'validation_url': validation_url,
        'qr_code': f"data:image/png;base64,{qr_base64}"
        }), 201

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

@app.route('/validate_ticket/<transaction_hmac>', methods=['GET'])
def validate_ticket(transaction_hmac):
    ticket = Ticket.query.filter_by(transaction_hmac=transaction_hmac).first()
    if ticket:
        expected_hmac = hmac.new(SECRET_KEY.encode(), ticket.transaction_id.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(transaction_hmac, expected_hmac):
            if ticket.scanned:
                return jsonify({'status': 'already_scanned'}), 400
            else:
                ticket.scanned = True
                db.session.commit()
                return jsonify({'status': 'valid', 'name': ticket.name, 'num_tickets': ticket.num_tickets}), 200
        else:
            return jsonify({'status': 'invalid_hmac'}), 403
    else:
        return jsonify({'status': 'invalid'}), 404

if __name__ == '__main__':
    app.run(debug=True)
