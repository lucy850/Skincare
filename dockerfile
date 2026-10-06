# Gunakan base image Python
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Salin file ke dalam container
COPY requirements.txt .
COPY app.py .

EXPOSE 5000


# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Jalankan aplikasi
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
