import requests
import numpy as np
import time
import json
import pandas as pd

API_URL = "http://3.90.36.143:5000/predict" 

print("Drift Attack...")


for i in range(100):
    
    mutated_income = max(0.5, 8.3252 + np.random.normal(loc=0.0, scale=5.0))
    
    mutated_age = max(1.0, 41.0 - abs(np.random.normal(loc=20.0, scale=10.0)))
    
    payload = {
        "MedInc": mutated_income,
        "HouseAge": mutated_age,
        "AveRooms": 6.9841,  
        "AveBedrms": 1.0238, 
        "Population": 322.0, 
        "AveOccup": 2.5556,  
        "Latitude": 37.88,   
        "Longitude": -122.23 
    }
    
    try:
        # API attack
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            print(f"[{i+1}/100] Injected: Income: {mutated_income:.2f} | Household age: {mutated_age:.1f}")
        else:
            print(f"API Error: {response.text}")
    except Exception as e:
        print(f"Server crashed! : {e}")
        break
        
    time.sleep(0.1)

print("Injected production_logs.csv!")