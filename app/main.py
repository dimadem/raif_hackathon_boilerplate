from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

from app.models import load_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Загружает модель при старте, освобождает ресурсы при остановке."""
    app.state.model = load_model()
    yield


app = FastAPI(title="Sentiment API", version="1.0.0", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Sentiment Analysis API"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/sentiment")
async def sentiment(request: Request, text: str):
    """
    Анализ тональности текста.

    Возвращает POSITIVE или NEGATIVE с confidence score.
    """
    result = request.app.state.model(text)[0]
    return {
        "text": text,
        "label": result["label"],
        "score": round(result["score"], 4),
    }
