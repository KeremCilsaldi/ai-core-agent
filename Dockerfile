# 1. Temel imaj: Hafif ve kararlı resmi Python 3.12 Linux imajı
FROM python:3.12-slim

# 2. Konteyner içindeki çalışma dizinini belirle
WORKDIR /app

# 3. Bağımlılık dosyasını içeri kopyala ve kütüphaneleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Proje kodlarımızı konteyner içine kopyala
COPY agent.py .
COPY main.py .

# 5. FastAPI'nin dışarıya açılacağı portu belirt (dokümantasyon amaçlı)
EXPOSE 8000

# 6. Konteyner başladığında Uvicorn sunucusunu 0.0.0.0 üzerinden ayağa kaldır
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]