"""
Загрузчик моделей.
Модели кэшируются в /app/model_cache (persistent volume).
"""

import os

os.environ["HF_HOME"] = "/app/model_cache"

def load_model():
    """Загружает модель sentiment analysis при старте приложения."""
    from transformers import pipeline

    return pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
    )
