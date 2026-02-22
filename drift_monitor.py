import os
import pandas as pd
import requests
from sklearn.datasets import fetch_california_housing
from evidently import Report
from evidently.presets import DataDriftPreset

def send_telegram_alert(message: str):
    """
    Send an alert message via Telegram Bot API.
    """
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id   = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Alert skipped: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("Telegram alert sent.")
    except requests.exceptions.RequestException as e:
        print(f"Telegram request failed: {e}")

def trigger_github_actions_ct_pipeline():
    """
    Trigger Continuous Training workflow on GitHub Actions via REST API.
    """
    github_owner = "nhatminh-115"
    github_repo = "cali-housing-mlops"
    workflow_filename = "mlops-ci.yml"

    github_token = os.environ.get("GITHUB_PAT")

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
        print("GitHub Actions CT pipeline triggered.")
    except requests.exceptions.RequestException as e:
        print(f"GitHub API request failed: {e}")
        if response.content:
            print(f"Details: {response.json()}")


def run_evidently_drift_check():
    print("Starting drift monitor...")

    # 1. Reference data: original training distribution
    data = fetch_california_housing(as_frame=True)
    reference_data = data.frame.drop('MedHouseVal', axis=1)

    # 2. Current data: live requests logged by Flask
    log_file = "production_logs.csv"
    if not os.path.exists(log_file):
        print(f"{log_file} not found. Run spammer.py first.")
        return
        
    current_data = pd.read_csv(log_file)

    # Keep only the 8 feature columns; drop metadata (timestamp, predicted_price)
    features = reference_data.columns.tolist()
    current_data = current_data[features]

    # 3. Run drift report
    drift_report = Report(metrics=[DataDriftPreset()])
    snapshot = drift_report.run(reference_data=reference_data, current_data=current_data)

    snapshot.save_html("drift_report.html")
    print("Report saved: drift_report.html")

    # 4. Parse results
    # Evidently 0.7: metrics[0]["value"] = {"count": N, "share": 0.x}
    report_json = snapshot.dict()
    drift_value = report_json["metrics"][0]["value"]
    share_of_drifted_columns = drift_value["share"]
    drift_share_threshold = 0.5  # default DataDriftPreset threshold
    dataset_drift = share_of_drifted_columns >= drift_share_threshold

    print(f"Drifted features: {share_of_drifted_columns * 100:.2f}%")

    # 5. Trigger alert if drift detected
    if dataset_drift:
        print("DATA DRIFT DETECTED")
        msg = (
            f"*SYSTEM ALERT: Data Drift Detected*\n"
            f"Drifted features: {share_of_drifted_columns * 100:.2f}%\n"
            f"Continuous retraining required."
        )
        send_telegram_alert(msg)
        trigger_github_actions_ct_pipeline()
    else:
        print("System stable. No drift detected.")

if __name__ == "__main__":
    run_evidently_drift_check()