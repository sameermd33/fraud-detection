from flask import Flask, request, jsonify, render_template
import numpy as np
import joblib

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
    
    # Return the prediction result
    return jsonify({"prediction": result_str})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
