import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# 1. Load Data thật (California Housing)
print("⏳ Dang tai du lieu...")
data = fetch_california_housing()
X = pd.DataFrame(data.data, columns=data.feature_names)
y = data.target

# 2. Split Data (80% Train, 20% Test) - ĐÂY LÀ BƯỚC TEST
# random_state=42 để kết quả lần nào chạy cũng giống nhau (Reproducibility)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"✅ Data loaded. Train size: {X_train.shape[0]}, Test size: {X_test.shape[0]}")

# 3. Train Model
print("⏳ Dang train model...")
model = LinearRegression()
model.fit(X_train, y_train)

# 4. EVALUATION (Kiểm định chất lượng) - QUAN TRỌNG
# Cho model thi thử trên tập Test (đề thi chưa từng gặp)
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("-" * 30)
print(f"📊 REPORT KET QUA MODEL:")
print(f"   - Mean Absolute Error (Sai so trung binh): {mae:.4f}")
print(f"   - R2 Score (Do chinh xac): {r2:.4f} (Cang gan 1 cang tot)")
print("-" * 30)

# 5. Save Model (Chỉ lưu nếu kết quả chấp nhận được)
if r2 > 0.5: # Ví dụ: Nếu độ chính xác > 50% mới lưu
    joblib.dump(model, 'housing_model.pkl')
    print("💾 Model da duoc luu thanh cong: housing_model.pkl")
else:
    print("⚠️ Model nhu hach, khong them luu!")