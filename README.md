# FastAPI Boilerplate

Шаблон FastAPI приложения с CI/CD пайплайном.

## Структура Docker

| Файл | Назначение |
|------|------------|
| `Dockerfile` | Production образ |
| `docker-compose.local.yml` | Локальная разработка с hot reload |

## Локальная разработка

```bash
docker compose -f docker-compose.local.yml up --build
```

Приложение будет доступно на http://localhost:8000

## CI/CD

При пуше тега вида `v*.*.*` автоматически:

1. Собирается Docker образ
2. Публикуется в GitHub Container Registry
3. Создаётся GitHub Release с changelog
4. Деплоится на сервер через SSH

### Создание релиза

```bash
git tag v1.0.0
git push origin v1.0.0
```

### Необходимые секреты GitHub

| Секрет | Описание |
|--------|----------|
| `PROD_SSH_HOST` | Адрес сервера |
| `PROD_SSH_USER` | SSH пользователь |
| `PROD_SSH_KEY` | SSH приватный ключ |

## ML модели

Модели загружаются при старте приложения и кэшируются в persistent volume `model_cache`.

### Добавление модели

1. Отредактируй `app/models.py` — функция `load_model()`
2. Добавь зависимости в `requirements.txt`

Пример с HuggingFace:

```python
from transformers import pipeline

def load_model():
    return pipeline("text-classification", model="your-model-name")
```

### Использование в роутах

```python
from fastapi import Request

@app.post("/predict")
async def predict(request: Request, text: str):
    model = request.app.state.model
    return model(text)
```

## API Endpoints

- `GET /` - Информация об API
- `GET /health` - Health check
- `POST /sentiment?text=your+text` - Анализ тональности текста

### Пример запроса

```bash
curl -X POST "http://localhost:8000/sentiment?text=I love this product"
```

Ответ:
```json
{"text": "I love this product", "label": "POSITIVE", "score": 0.9998}
```
