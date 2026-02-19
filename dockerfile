FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Thuc thi Continuous Training (CT) ngay tai thoi diem Build Image
RUN python train.py

EXPOSE 5000

CMD ["python", "app.py"]