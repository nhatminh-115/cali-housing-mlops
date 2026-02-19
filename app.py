from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import logging

# Thiet lap logging de theo doi he thong
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Load model vao memory ngay khi khoi dong server
try:
    model = joblib.load('housing_model.pkl')
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model: {e}")
    model = None

@app.route('/')
def home():
    # Tra ve giao dien UI cho nguoi dung
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({'error': 'Model is not available.'}), 500

    try:
        data = request.get_json()
        
        # Chuyen doi du lieu JSON thanh Numpy array (Vector x)
        features = np.array([[
            data['MedInc'],
            data['HouseAge'],
            data['AveRooms'],
            data['AveBedrms'],
            data['Population'],
            data['AveOccup'],
            data['Latitude'],
            data['Longitude']
        ]], dtype=float)
        
        # Thuc hien phep toan ma tran de du doan (y_hat)
        prediction = model.predict(features)[0]
        
        # Gioi han gia tri du doan khong am
        prediction = max(0.0, float(prediction))
        
        return jsonify({'predicted_price_usd': prediction * 100000}) # Nhan 100k de ra gia thuc te
        
    except KeyError as e:
        return jsonify({'error': f'Missing feature: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)