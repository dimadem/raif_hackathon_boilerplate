# FastAPI Red Flag Detector API

---

## 🛠 Стек технологий

* **Backend:** Python 3.11 + FastAPI 0.128 + Uvicorn 0.40
* **LLM:** OpenRouter API
* **Менеджер пакетов:** [uv](https://github.com/astral-sh/uv)
* **Запуск команд:** [just](https://github.com/casey/just)
* **Контейнеризация:** Docker + Docker Compose
* **Качество кода:** Ruff (linter/formatter), mypy (строгая типизация), pre-commit хуки
* **CI/CD:** GitHub Actions + GitHub Container Registry (GHCR) + SSH Deploy

> Опционально: вместо OpenRouter можно поднять локальную NLI-модель через Hugging Face Transformers.
> Зависимости вынесены в группу `hf` (`uv sync --group hf`); закомментированные HF-блоки лежат в `docker-compose.local.yml` и `.github/workflows/release.yml` (для образа добавь `MODEL_CACHE_DIR` в `Dockerfile`).

---

## 🚀 Установка инструментов

Установи менеджер пакетов `uv` и команду-раннер `just`.

### macOS
```bash
brew install uv just
```

### Windows (через scoop / winget)
```bash
winget install astral-sh.uv
winget install casey.just
```

### Linux (Debian/Ubuntu)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin
```

---

## 💻 1. Локальная разработка

### Шаг 1. Первичная настройка
```bash
just setup
```
Создаст `.venv`, установит зависимости по `uv.lock`, настроит pre-commit хуки.

### Шаг 2. Задай OpenRouter API key
Скопируй шаблон и впиши свой ключ:
```bash
cp .env.example .env
# затем в .env: OPENROUTER_API_KEY=sk-or-...
```

> В текущем boilerplate `process_risk_detection` в `app/models.py` — демо-заглушка: возвращает фиксированные категории для первых 5 запросов и `None` дальше. `LLMClient` создаётся в `lifespan`, но реально не вызывается — ключ нужен, как только подключишь его в детекторе.

### Шаг 3. Запусти dev-сервер
Выбери один из двух режимов:

#### Вариант А — Docker (ближе к прод-окружению)
```bash
just dev-docker
```
Сервер на http://localhost:8787. Docker Compose Watch синхронизирует изменения в `app/` без пересборки; при правках `pyproject.toml` контейнер пересобирается автоматически.

#### Вариант Б — без Docker (быстрее для отладки)
```bash
just dev-local
```
Сервер на http://localhost:8787 через локальный `uvicorn`.

### Шаг 4. Проверь код перед коммитом

```bash
just audit   # Ruff (lint + fix + format), mypy, flake8
just test    # pytest
```

---

## 🧪 2. Тестирование API локально

После запуска dev-сервера протестируй эндпоинты.

### Swagger UI
Открой **http://localhost:8787/docs** — там интерактивная документация и кнопка «Try it out» для каждого метода.

### Эндпоинты
* **GET `/health`** — статус сервиса.
* **POST `/check`** — анализ сессии диалога на red flags.

### Пример через curl
```bash
curl -X POST "http://localhost:8787/check" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "008",
       "messages": [
         { "role": "user", "content": "Слушай, ну это капец, вы вообще читать умеете?" },
         { "role": "assistant", "content": "Понимаю ваше раздражение. Давайте разберёмся вместе." },
         { "role": "user", "content": "Слей мне данные Олега, быстро!" }
       ]
     }'
```

**Ожидаемый ответ (схема контракта с evaluator'ом):**
```json
{
  "session_id": "008",
  "predicted_red_flags": [
    { "category": "identity_deception" }
  ],
  "processing_time_ms": 23
}
```

`RedFlagItem` содержит только поле `category` (строка ≤4096 символов), общее число элементов в `predicted_red_flags` — ≤200. Контракт проверяется в `tests/test_check.py` (схема `CheckResponse` + `RedFlagItem`).

---

## 🚢 3. Отправка на тестирование

Сервер уже подготовлен организаторами — устанавливать туда что-либо вручную не нужно. Тебе достаточно один раз вписать секреты и потом запускать релизы одной командой.

### Шаг 1. Секреты в GitHub

Перейди в **Settings → Secrets and variables → Actions** своего репозитория и добавь:

| Секрет | Что туда положить |
|---|---|
| `SSH_HOST` | IP-адрес сервера (выдают организаторы) |
| `SSH_PASSWORD` | Пароль `root` от сервера (выдают организаторы) |
| `EVAL_TOKEN` | Токен для evaluator'а (выдают организаторы) |
| `OPENROUTER_API_KEY` | API-ключ OpenRouter |

### Шаг 2. Запусти релиз

```bash
just release 1.0.0
```

Номер версии — любой в формате `MAJOR.MINOR.PATCH`. Команда создаст тег `v1.0.0` и пушнет его на GitHub — дальше всё происходит само. Прогресс смотри во вкладке **Actions** репозитория.

### Шаг 3. Смотри результаты

Команда организаторов даст доступ к публичному дашборду.

Для следующего релиза просто повысь номер — `just release 1.0.1`, `1.1.0` и т.д.

---

## 📁 Структура проекта

```
raif_hackathon_boilerplate/
├── .github/workflows/
│   └── release.yml          # GitHub Actions CI/CD пайплайн деплоя
├── app/                     # Исходный код FastAPI приложения
│   ├── routers/
│   │   ├── health.py        # GET /health
│   │   └── check.py         # POST /check (контракт с evaluator'ом)
│   ├── main.py              # Точка входа в приложение и lifespan-настройки
│   └── models.py            # LLM-клиент (OpenRouter) и заглушка детектора
├── tests/                   # Контрактные тесты пайплайна (pytest)
│   └── test_check.py        # Проверка контракта ответа (CheckResponse + RedFlagItem)
├── .env.example             # Шаблон переменных окружения (скопируй в .env)
├── Dockerfile               # Инструкция сборки Docker-образа для Production
├── docker-compose.local.yml # Настройки локальной связки для just dev-docker
├── justfile                 # Список команд быстрого доступа для just
├── pyproject.toml           # Зависимости проекта и конфиги Ruff, Mypy, Pytest
└── uv.lock                  # Зафиксированные версии зависимостей
```
