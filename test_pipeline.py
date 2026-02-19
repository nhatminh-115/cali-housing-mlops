import pytest
import json
import numpy as np
from unittest.mock import MagicMock
import app as flask_app

@pytest.fixture
def client():
    """
    Khoi tao moi truong kiem thu cach ly (Hermetic Test Fixture).
    Su dung ky thuat Mocking de gia lap mo hinh toan hoc, loai bo su phu thuoc vao file I/O.
    """
    # 1. Khoi tao mo hinh gia lap (Mock Object)
    mock_model = MagicMock()
    
    # 2. Xac dinh hanh vi: Ham predict luon tra ve mot vector Numpy chua hang so 4.526
    mock_model.predict.return_value = np.array([4.526])
    
    # 3. Tiem phu thuoc (Inject): Ghi de bien 'model' toan cuc trong file app.py bang mo hinh gia
    flask_app.model = mock_model
    
    # Khoi tao test client
    flask_app.app.config['TESTING'] = True
    with flask_app.app.test_client() as client:
        yield client

def test_home_page(client):
    """
    Kiem tra chot chan Frontend.
    Dam bao DOM duoc tra ve voi ma trang thai 200.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"<title>Cali Housing Predictor</title>" in response.data

def test_predict_api_valid(client):
    """
    Kiem tra chu trinh tich chap du lieu (Data Serialization).
    Truyen vector x vao API va ky vong he thong tra ve gia tri tu ham Mock.
    """
    payload = {
        "MedInc": 8.3252,
        "HouseAge": 41.0,
        "AveRooms": 6.9841,
        "AveBedrms": 1.0238,
        "Population": 322.0,
        "AveOccup": 2.5556,
        "Latitude": 37.88,
        "Longitude": -122.23
    }
    
    response = client.post('/predict', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'predicted_price_usd' in data
    assert isinstance(data['predicted_price_usd'], float)

def test_predict_api_missing_feature(client):
    """
    Kiem tra co che kiem soat ngoai le (Exception Handling).
    Nhan tao loi khuyet thieu chieu du lieu va ky vong bat duoc HTTP 400.
    """
    payload = {
        "MedInc": 8.3252,
        "HouseAge": 41.0
    }
    
    response = client.post('/predict', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data