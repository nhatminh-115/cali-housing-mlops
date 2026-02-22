from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import logging
import csv
from datetime import datetime
import pandas as pd

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
        features = pd.DataFrame([{
            'MedInc': data['MedInc'],
            'HouseAge': data['HouseAge'],
            'AveRooms': data['AveRooms'],
            'AveBedrms': data['AveBedrms'],
            'Population': data['Population'],
            'AveOccup': data['AveOccup'],
            'Latitude': data['Latitude'],
            'Longitude': data['Longitude']
        }])
        
        # Thuc hien phep toan ma tran de du doan (y_hat)
        prediction = model.predict(features)[0]
        
        # Gioi han gia tri du doan khong am
        prediction = max(0.0, float(prediction))

        # Ghi toan bo du lieu nguoi dung vao file CSV de theo doi production
        log_file = "production_logs.csv"
        log_data = {
            'MedInc': data['MedInc'],
            'HouseAge': data['HouseAge'],
            'AveRooms': data['AveRooms'],
            'AveBedrms': data['AveBedrms'],
            'Population': data['Population'],
            'AveOccup': data['AveOccup'],
            'Latitude': data['Latitude'],
            'Longitude': data['Longitude'],
            'timestamp': datetime.now().isoformat(),
            'predicted_price': prediction * 100000
        }

        # Viet noi (Append) vao file log
        with open(log_file, mode='a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=log_data.keys())
            # Neu file trong thi ghi Header
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(log_data)

        return jsonify({'predicted_price_usd': prediction * 100000}) # Nhan 100k de ra gia thuc te
        
    except KeyError as e:
        return jsonify({'error': f'Missing feature: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)