import os
import logging
import pandas as pd
from flask import Flask, request, jsonify, render_template
from supabase import create_client, Client
import mlflow.pyfunc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# 1. Cloud Infrastructure Initialization
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
    logging.warning("Supabase configuration missing. Cloud Telemetry is disabled.")

# 2. Dynamic Model Loading via MLflow Registry
MLFLOW_URI = os.environ.get("MLFLOW_TRACKING_URI")
model = None

if MLFLOW_URI:
    try:
        import mlflow
        mlflow.set_tracking_uri(MLFLOW_URI)
        
        # Target the latest version of the registered model
        model_name = "Cali_Housing_Production_Model"
        model_uri = f"models:/{model_name}/latest"
        
        logging.info(f"Establishing connection to Model Registry: {model_uri}")
        model = mlflow.pyfunc.load_model(model_uri)
        logging.info("Model payload dynamically loaded and ready for inference.")
    except Exception as e:
        logging.error(f"Failed to fetch model artifact from Registry: {e}")
else:
    logging.error("Critical: MLFLOW_TRACKING_URI is undefined. Inference service degraded.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({'error': 'Inference engine is currently unavailable due to missing model artifact.'}), 503

    try:
        data = request.get_json()
        
        # Enforce Schema structure
        features = pd.DataFrame([{
            'MedInc': float(data['MedInc']),
            'HouseAge': float(data['HouseAge']),
            'AveRooms': float(data['AveRooms']),
            'AveBedrms': float(data['AveBedrms']),
            'Population': float(data['Population']),
            'AveOccup': float(data['AveOccup']),
            'Latitude': float(data['Latitude']),
            'Longitude': float(data['Longitude'])
        }])
        
        # Execute Inference
        prediction = model.predict(features)[0]
        prediction_usd = max(0.0, float(prediction) * 100000)

        # Execute Telemetry Logging (Sliding Window Data Source)
        if supabase:
            try:
                log_data = features.iloc[0].to_dict()
                log_data['predicted_price'] = prediction_usd
                supabase.table("production_logs").insert(log_data).execute()
                logging.info("Inference payload successfully transmitted to Data Warehouse.")
            except Exception as e:
                logging.error(f"Telemetry transmission failure: {e}")

        return jsonify({'predicted_price_usd': prediction_usd})

    except Exception as e:
        return jsonify({'error': f"Payload validation failed: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)