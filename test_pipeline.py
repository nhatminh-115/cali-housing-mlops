import pytest
import json
from app import app

@pytest.fixture
def client():
    """
    Khoi tao moi truong kiem thu (Test Fixture).
    Gia lap mot client de gui cac HTTP request ma khong can khoi dong server that.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """
    Kiem tra khoi Frontend (Giao dien).
    Xac thuc route '/' hoat dong (200 OK) va render dung file HTML.
    """
    response = client.get('/')
    assert response.status_code == 200
    # Kiem tra su ton tai cua the title de xac nhan DOM duoc load thanh cong
    assert b"<title>Cali Housing Predictor</title>" in response.data

def test_predict_api_valid(client):
    """
    Kiem tra khoi Model Inference.
    Xac thuc API co the tiep nhan vector dac trung x va tra ve du doan y_hat.
    """
    # Dinh nghia vector dau vao x
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
    
    # Gui POST request voi payload duoc Serialize thanh JSON
    response = client.post('/predict', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Xac thuc ket qua tra ve phai chua tu khoa 'predicted_price_usd' va phai la so thuc (float)
    assert 'predicted_price_usd' in data
    assert isinstance(data['predicted_price_usd'], float)

def test_predict_api_missing_feature(client):
    """
    Kiem tra co che xu ly ngoai le (Exception Handling).
    Khi client gui thieu dac trung, he thong phai bat duoc KeyError va tra ve loi 400.
    """
    # Vector x bi khuyet du lieu
    payload = {
        "MedInc": 8.3252,
        "HouseAge": 41.0
    }
    
    response = client.post('/predict', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    # Xac thuc HTTP Status Code la 400 (Bad Request) thay vi 500 (Internal Server Error)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data