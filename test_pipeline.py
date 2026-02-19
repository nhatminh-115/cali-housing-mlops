import os
import joblib
import pandas as pd
from sklearn.metrics import r2_score
from app import app
import pytest

# Biến toàn cục để lưu model sau khi train
MODEL_PATH = 'housing_model.pkl'

def test_model_training_quality():
    """
    Test 1: Train thử model và kiểm tra xem R2 Score có > 0.5 không.
    Đây là 'Model Quality Gate'.
    """
    # 1. Chạy training script (Import hàm train hoặc chạy lệnh os)
    # Ở đây ta giả lập việc chạy train.py bằng cách import code train
    # (Để đơn giản, bro có thể dùng os.system để gọi train.py)
    exit_code = os.system("python3 train.py")
    assert exit_code == 0, "Qua trinh Training bi crash!"

    # 2. Kiểm tra file model có được tạo ra không
    assert os.path.exists(MODEL_PATH), "File model.pkl khong ton tai sau khi train!"

    # 3. Load model lên để test chỉ số
    model = joblib.load(MODEL_PATH)
    
    # Load data test (Lấy tạm vài dòng từ data thật để test nhanh)
    from sklearn.datasets import fetch_california_housing
    from sklearn.model_selection import train_test_split
    
    data = fetch_california_housing()
    X = pd.DataFrame(data.data, columns=data.feature_names)
    y = data.target
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Predict và tính điểm
    y_pred = model.predict(X_test)
    score = r2_score(y_test, y_pred)
    
    print(f" -> Test R2 Score: {score}")
    
    # ASSERTION: Nếu Score < 0.5 thì FAIL ngay lập tức -> GitHub báo đỏ
    assert score > 0.5, f"Model qua te! R2 Score {score} < 0.5"

@pytest.fixture
def client():
    """Tạo một client giả lập để test Flask API"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_api_prediction(client):
    """
    Test 2: Gửi request giả vào API xem nó có trả về JSON đúng không
    """
    # Payload giả định
    payload = {
        "MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.9841, "AveBedrms": 1.0238,
        "Population": 322.0, "AveOccup": 2.5556, "Latitude": 37.88, "Longitude": -122.23
    }
    
    # Gửi POST request
    response = client.post('/predict', json=payload)
    
    # Check 1: Phải trả về 200 OK
    assert response.status_code == 200, "API sap hoac tra ve loi!"
    
    # Check 2: Phải có key 'predicted_price_usd'
    json_data = response.get_json()
    assert 'predicted_price_usd' in json_data