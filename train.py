import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# 1. Load Data (California Housing)
print("Data Loading...")
data = fetch_california_housing()
X = pd.DataFrame(data.data, columns=data.feature_names)
y = data.target

# 2. Split Data 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"✅ Data loaded. Train size: {X_train.shape[0]}, Test size: {X_test.shape[0]}")

# 3. Train Model
print("Training...")
model = LinearRegression()
model.fit(X_train, y_train)

# 4. EVALUATION 
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("-" * 30)
print(f"Model Report:")
print(f"   - Mean Absolute Error: {mae:.4f}")
print(f"   - R2 Score: {r2:.4f}")
print("-" * 30)

# 5. Save Model
if r2 > 0.5: 
    joblib.dump(model, 'housing_model.pkl')
    print("Saved: housing_model.pkl")
else:
    print("Bad model quality - not saved!")