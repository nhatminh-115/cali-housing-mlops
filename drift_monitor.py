import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from sklearn.datasets import fetch_california_housing
from evidently import Report
from evidently.presets import DataDriftPreset
from supabase import create_client, Client
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 1. Thiet lap Ket noi Supabase (Database Connection)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing required environment variables: SUPABASE_URL, SUPABASE_KEY.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_recent_production_logs() -> pd.DataFrame:
    """
    Fetch production logs from Supabase using a 24-hour sliding window.
    """
    logging.info("Querying production logs from Supabase...")

    # Compute T-24h threshold in ISO 8601 format for PostgreSQL compatibility
    time_threshold = (datetime.utcnow() - timedelta(days=1)).isoformat()

    try:
        response = supabase.table("production_logs") \
            .select("*") \
            .gte("created_at", time_threshold) \
            .execute()

        data = response.data
        if not data:
            logging.info("No new records in the last 24 hours. Skipping drift check.")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        logging.info(f"Fetched {len(df)} records from production.")
        return df

    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return pd.DataFrame()

def trigger_github_actions_ct_pipeline():
    """
    Trigger Continuous Training workflow via GitHub Actions REST API.
    """
    github_owner = "nhatminh-115"
    github_repo = "cali-housing-mlops"
    workflow_filename = "mlops-ct.yml"

    github_token = os.environ.get("GITHUB_PAT")
    if not github_token:
        logging.warning("GITHUB_PAT not set. CT pipeline trigger skipped.")
        return

    url = f"https://api.github.com/repos/{github_owner}/{github_repo}/actions/workflows/{workflow_filename}/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    payload = {"ref": "main"}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logging.info("CT pipeline triggered via GitHub Actions.")
    except requests.exceptions.RequestException as e:
        logging.error(f"GitHub API request failed: {e}")

def run_evidently_drift_check():
    # 1. Fetch current production data
    current_data = fetch_recent_production_logs()

    if current_data.empty:
        return

    # 2. Load reference data (original training distribution)
    logging.info("Loading California Housing reference dataset...")
    data = fetch_california_housing(as_frame=True)
    reference_data = data.frame.drop('MedHouseVal', axis=1)

    # Drop DB metadata columns; keep only the 8 feature columns
    features = reference_data.columns.tolist()
    current_data_features = current_data[features]

    # 3. Run statistical drift analysis
    logging.info("Running Evidently drift report...")
    drift_report = Report(metrics=[DataDriftPreset()])
    snapshot = drift_report.run(reference_data=reference_data, current_data=current_data_features)

    snapshot.save_html("drift_report.html")
    logging.info("Report saved: drift_report.html")

    # 4. Parse results (Evidently 0.7: metrics[0]["value"] = {"count": N, "share": 0.x})
    report_json = snapshot.dict()
    drift_value = report_json["metrics"][0]["value"]
    share_of_drifted_columns = drift_value["share"]
    dataset_drift = share_of_drifted_columns >= 0.5  # default DataDriftPreset threshold

    logging.info(f"Drifted features: {share_of_drifted_columns * 100:.2f}%")

    # 5. Conditional alert
    if dataset_drift:
        logging.warning("Data drift detected. Triggering CT pipeline.")
        trigger_github_actions_ct_pipeline()
    else:
        logging.info("No drift detected. Distribution is stable.")

if __name__ == "__main__":
    run_evidently_drift_check()