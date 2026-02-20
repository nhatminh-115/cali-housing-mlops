import os
import numpy as np
import pandas as pd
import requests

def calculate_psi(expected: pd.Series, actual: pd.Series, bins: int = 10) -> float:
    breakpoints = np.arange(0, bins + 1) / bins * 100
    bin_edges = np.percentile(expected, breakpoints)
    bin_edges = np.unique(bin_edges)
    
    expected_percents = np.histogram(expected, bins=bin_edges)[0] / len(expected)
    actual_percents = np.histogram(actual, bins=bin_edges)[0] / len(actual)
    
    epsilon = 1e-4
    expected_percents = np.where(expected_percents == 0, epsilon, expected_percents)
    actual_percents = np.where(actual_percents == 0, epsilon, actual_percents)
    
    psi_values = (actual_percents - expected_percents) * np.log(actual_percents / expected_percents)
    return float(np.sum(psi_values))

def send_telegram_alert(message: str):
    """
    Thuc thi giao thuc HTTP POST de day Payload (thong bao) qua RESTful API cua Telegram.
    Ap dung co che bat loi (Exception Handling) de bao ve luong thuc thi chinh.
    """
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Bo qua buoc Alert: Chua tim thay phien ban bien moi truong Telegram.")
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
        print("Da truyen tai canh bao qua Telegram thanh cong.")
    except requests.exceptions.RequestException as e:
        print(f"Loi mang khi ket noi den Telegram API: {e}")

def simulate_and_detect_drift(original_df: pd.DataFrame):
    serving_df = original_df.copy()
    serving_df['MedInc'] = serving_df['MedInc'] * 1.5 
    serving_df['HouseAge'] = serving_df['HouseAge'] + 15
    
    report_lines = ["SYSTEM MONITORING\n"]
    is_drifted = False
    
    for column in original_df.columns:
        psi_score = calculate_psi(original_df[column], serving_df[column])
        
        if psi_score < 0.1:
            status = "🟢 Stable"
        elif psi_score < 0.2:
            status = "🟡 Warning"
        else:
            status = "🔴 Drift Detected"
            is_drifted = True
            
        report_lines.append(f"- *{column}*: {psi_score:.4f} ({status})")
        
    final_report = "\n".join(report_lines)
    print(final_report)
    
    if is_drifted:
        final_report += "\n\n*ALERT*: Data drift detected in the serving environment. Immediate investigation is recommended."
        send_telegram_alert(final_report)

if __name__ == "__main__":
    from sklearn.datasets import fetch_california_housing
    data = fetch_california_housing(as_frame=True).frame
    X_train = data.drop('MedHouseVal', axis=1)
    simulate_and_detect_drift(X_train)