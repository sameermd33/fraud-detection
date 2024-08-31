from flask import Flask, request, jsonify, render_template
import numpy as np
import joblib

app = Flask(__name__)

# Load the Random Forest model for each peer
peer1_model = joblib.load('model_peer1.pkl')
peer2_model = joblib.load('model_peer2.pkl')
peer3_model = joblib.load('model_peer3.pkl')

# Store the valid passwords
peer_passwords = {
    "peer1": "iampeer1",
    "peer2": "iampeer2",
    "peer3": "iampeer3"
}

def verify_password(provided_password):
    for peer, valid_password in peer_passwords.items():
        if provided_password == valid_password:
            return peer
    return None

def predict_fraud(model, features):
    # Create a numpy array with the input data
    input_data = np.array(features).reshape(1, -1)
    
    # Make a prediction using the provided model
    prediction = model.predict(input_data)
    
    # Return the prediction
    return prediction[0]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    password = data.get('password')
    features = data.get('features')

    if not features:
        return jsonify({"error": "No features provided"}), 400

    peer = verify_password(password)
    if peer == "peer1":
        model = peer1_model
    elif peer == "peer2":
        model = peer2_model
    elif peer == "peer3":
        model = peer3_model
    else:
        return jsonify({"error": "Authentication of Peer Failed"}), 401

    # Predict the fraud status
    result = predict_fraud(model, features)
    result_str = "Fraud" if result == 1.0 else "Not Fraud"
    
    return jsonify({"prediction": result_str})

if __name__ == '__main__':
    app.run(debug=True)
