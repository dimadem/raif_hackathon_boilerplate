FROM python:3.11-slim

WORKDIR /app

# Директория для кэша моделей (монтируется как volume)
ENV MODEL_CACHE_DIR=/app/model_cache
RUN mkdir -p $MODEL_CACHE_DIR

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
