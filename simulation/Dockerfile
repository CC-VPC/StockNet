FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY cron_price_update.py .

CMD ["python", "-u", "cron_price_update.py"]
