FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY app.py stations_data.json ./

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
