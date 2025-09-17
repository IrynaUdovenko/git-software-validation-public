FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*
COPY . /app
CMD ["uvicorn", "api.main:app", "--host","0.0.0.0","--port","8000"]
