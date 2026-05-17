FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg libgl1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY services/api /app/services/api
COPY data /app/data
ENV PYTHONPATH=/app/services/api
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
