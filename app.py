from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load model
try:
    model = joblib.load('housing_model.pkl')
except:
    print("⚠️ Khong tim thay model. Hay chay train.py truoc!")

@app.route('/')
def home():
    return "<h1>California Housing Price Prediction API 🏠</h1>"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Lấy dữ liệu JSON client gửi lên
        data = request.get_json()
        
        # Dataset California cần 8 tham số đầu vào theo thứ tự:
        # MedInc, HouseAge, AveRooms, AveBedrms, Population, AveOccup, Latitude, Longitude
        features = [
            data['MedInc'],
            data['HouseAge'],
            data['AveRooms'],
            data['AveBedrms'],
            data['Population'],
            data['AveOccup'],
            data['Latitude'],
            data['Longitude']
        ]
        
        # Dự đoán
        prediction = model.predict([features])
        
        # Giá nhà ở Cali tính theo đơn vị $100,000
        price_in_usd = prediction[0] * 100000 
        
        return jsonify({
            'predicted_price_usd': round(price_in_usd, 2),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)