import os
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature

# 1. MLflow Configuration
MLFLOW_URI = os.environ.get("MLFLOW_TRACKING_URI")
if not MLFLOW_URI:
    raise ValueError("Architecture Error: MLFLOW_TRACKING_URI environment variable is missing.")

mlflow.set_tracking_uri(MLFLOW_URI)
mlflow.set_experiment("Cali_Housing_CT_Pipeline")

print("Initiating Data Ingestion...")
data = fetch_california_housing()
X = pd.DataFrame(data.data, columns=data.feature_names)
y = data.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Data ingestion completed. Train capacity: {X_train.shape[0]}, Test capacity: {X_test.shape[0]}")

# 2. Continuous Training & Model Registration
with mlflow.start_run():
    print("Executing Model Training Phase...")
    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("-" * 30)
    print("Evaluation Metrics:")
    print(f"   - Mean Absolute Error: {mae:.4f}")
    print(f"   - R2 Score: {r2:.4f}")
    print("-" * 30)

    mlflow.log_metric("mae", mae)
    mlflow.log_metric("r2", r2)

    # 3. Model Registry Integration
    if r2 > 0.5:
        # Enforce Data Contract via Model Signature
        signature = infer_signature(X_train, y_pred)
        
        # Serialize and register model to DagsHub MLflow Registry
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            signature=signature,
            registered_model_name="Cali_Housing_Production_Model"
        )
        print("Model successfully serialized and registered to MLflow Model Registry.")
    else:
        print("Validation Failed: Model quality below threshold. Artifact discarded.")