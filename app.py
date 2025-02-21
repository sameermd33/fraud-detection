from flask import Flask, request, jsonify, render_template
import numpy as np
import joblib
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Load the Random Forest model for each peer
peer1_model = joblib.load('model_peer1.pkl')
peer2_model = joblib.load('model_peer2.pkl')
peer3_model = joblib.load('model_peer3.pkl')

# Store the valid passwords for each peer
peer_passwords = {
    "peer1": "iampeer1",
    "peer2": "iampeer2",
    "peer3": "iampeer3"
}

# List of possible fraud reasons based on dataset features
fraud_reasons = [
    "Transaction location is too far from home.",
    "Transaction distance from the last transaction is unusually high.",
    "Purchase price is much higher than the median purchase price.",
    "Retailer is frequently repeated, which is unusual.",
    "Card was used without a chip, increasing fraud likelihood.",
    "Card was used without a PIN, making it vulnerable to fraud.",
    "Transaction was made online, which has a higher risk.",
]

def send_fraud_alert():
    """
    Send an email notification when fraud is detected.
    """
    sender_email = "sameermd12q@gmail.com"  # Your email
    sender_password = "hardikpandya"  # Your email password
    receiver_email = "aakhilshaikooo9@gmail.com"  # Fixed receiver email

    subject = "Fraudulent Transaction Alert"
    reason = random.choice(fraud_reasons)  # Pick a random fraud reason
    body = f"""
    Alert! A fraudulent transaction has been detected.

    Reason: {reason}

    Please verify the transaction immediately.
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())  # Sending to fixed receiver email
        server.quit()
        print(f"Fraud alert email sent to {receiver_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

def verify_password(provided_password):
    """
    Verify the password and return the corresponding peer identifier if valid.
    """
    for peer, valid_password in peer_passwords.items():
        if provided_password == valid_password:
            return peer
    return None

def predict_fraud(model, features):
    """
    Predict fraud based on the given features using the specified model.
    """
    input_data = np.array(features).reshape(1, -1)
    prediction = model.predict(input_data)
    return prediction[0]

@app.route('/')
def home():
    """
    Serve the home page for the web application.
    """
    return render_template('home.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Handle the POST request to predict fraud based on the provided features and password.
    """
    data = request.json
    password = data.get('password')
    features = data.get('features')

    # Validate if features are provided in the request
    if not features:
        return jsonify({"error": "No features provided"}), 400

    # Authenticate the peer using the password
    peer = verify_password(password)
    if peer == "peer1":
        model = peer1_model
    elif peer == "peer2":
        model = peer2_model
    elif peer == "peer3":
        model = peer3_model
    else:
        return jsonify({"error": "Authentication of Peer Failed"}), 401

    # Predict the fraud status using the corresponding peer's model
    result = predict_fraud(model, features)
    result_str = "Fraud" if result == 1.0 else "Not Fraud"
    response = {"prediction": result_str}

    # If fraud is detected, send an email alert
    if result == 1.0:
        send_fraud_alert()  # Sending fraud alert

    return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
