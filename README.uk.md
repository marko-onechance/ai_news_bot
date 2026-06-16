![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136.3-009688?logo=fastapi&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.6.3-37814A?logo=celery&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.13-FF6600?logo=rabbitmq&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-2.41.1-412991?logo=openai&logoColor=white)
![Telethon](https://img.shields.io/badge/Telethon-1.43.2-2CA5E0?logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

# AI News Bot для Telegram

[English](README.md) · **Українська**

Сервіс, який збирає новини з веб-сайтів та публічних Telegram-каналів, фільтрує та дедуплікує їх, генерує яскраві пости через OpenAI GPT-4o та публікує їх у Telegram-канал — усе керується через REST API зі Swagger-документацією.

---

## Зміст

- [Функціональність](#функціональність)
- [Структура проєкту](#структура-проєкту)
- [Запуск](#запуск)
- [Змінні оточення](#змінні-оточення)
- [API-ендпоінти](#api-ендпоінти)
- [Pipeline](#pipeline)
- [Чек-ліст](#чек-ліст)

---

## Функціональність

| # | Функція | Технологія |
|---|---------|-----------|
| 1 | Збір новин із сайтів | Celery Beat, requests, BeautifulSoup |
| 2 | Збір новин із Telegram-каналів | Celery Beat, Telethon |
| 3 | Фільтрація за ключовими словами | Python, PostgreSQL |
| 4 | Дедуплікація новин | PostgreSQL UNIQUE constraints |
| 5 | AI-генерація постів | OpenAI GPT-4o |
| 6 | Публікація в Telegram | Telethon |
| 7 | REST API (CRUD джерела, ключові слова) | FastAPI |
| 8 | Перегляд постів та логів помилок | FastAPI |
| 9 | Ручна генерація через API | FastAPI + OpenAI |
| 10 | Swagger-документація | FastAPI `/docs` |
| 11 | Моніторинг черги | Celery Flower |

---

## Структура проєкту

```
.
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Налаштування (pydantic-settings)
│   ├── db.py                # Async + Sync SQLAlchemy engines
│   ├── models.py            # ORM моделі: Source, NewsItem, Keyword, Post
│   ├── tasks.py             # Celery tasks pipeline
│   ├── utils.py             # Налаштування логування
│   ├── api/
│   │   ├── endpoints.py     # FastAPI роутери
│   │   └── schemas.py       # Pydantic схеми
│   ├── ai/
│   │   ├── openai_client.py # OpenAI client singleton
│   │   └── generator.py     # Генерація постів з retry логікою
│   ├── news_parser/
│   │   ├── sites.py         # HTML парсер сайтів (BeautifulSoup)
│   │   └── telegram.py      # Парсер Telegram-каналів (Telethon)
│   └── telegram/
│       └── publisher.py     # Публікатор у Telegram (Telethon)
├── celery_worker.py         # Celery app + Beat розклад
├── docker-compose.yml       # Вся інфраструктура
├── Dockerfile
├── generate_session.py      # Файл для генерації сесії  
├── requirements.txt
└── .env.example
```

---

## Запуск

### 1. Клонуйте репозиторій та налаштуйте `.env`

```bash
git clone <repo-url>
cd 1_ai_new_bot
cp .env.example .env
# Відредагуйте .env — вкажіть ключі OpenAI та Telegram
```

### 2. Авторизація в Telegram (Обов'язково для публікації)

Оскільки Docker працює у фоні, потрібно локально згенерувати файл сесії Telegram, щоб Telethon міг підключатися без інтерактивного запиту коду.

```bash
# Створіть віртуальне середовище та встановіть залежності
python -m venv venv
source venv/bin/activate
pip install telethon python-dotenv

# Запустіть скрипт авторизації
python generate_session.py
```
*Введіть свій номер телефону та код з Telegram. Це створить файл `.session`, який відповідає змінній `TELEGRAM_SESSION`.*

### 3. Запустіть усі сервіси через Docker Compose

```bash
docker-compose up --build
```

Це підніме:
- **FastAPI** → http://localhost:8000
- **Swagger UI** → http://localhost:8000/docs
- **RabbitMQ Management** → http://localhost:15672 (guest/guest)
- **Celery Flower** → http://localhost:5555
- **PostgreSQL** → localhost:5432
- **Redis** → localhost:6379

### 4. (Опційно) Локальний запуск без Docker

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Запустіть PostgreSQL, RabbitMQ, Redis окремо, потім:
uvicorn app.main:app --reload --port 8000 &
celery -A celery_worker.celery_app worker --loglevel=info &
celery -A celery_worker.celery_app beat --loglevel=info
```

---

## Змінні оточення

Скопіюйте `.env.example` → `.env` і заповніть:

| Змінна | Опис | Приклад |
|--------|------|---------|
| `PG_USERNAME` | PostgreSQL користувач | `ainewsbot` |
| `PG_PASSWORD` | PostgreSQL пароль | `postgres` |
| `PG_HOST` | PostgreSQL хост | `postgres` (Docker) / `localhost` |
| `PG_NAME` | PostgreSQL база даних | `ainewsbot` |
| `RABBITMQ_URL` | URL брокера RabbitMQ | `amqp://guest:guest@rabbitmq:5672//` |
| `REDIS_URL` | URL Redis (backend Celery) | `redis://redis:6379/0` |
| `TELEGRAM_API_ID` | Telegram API ID (my.telegram.org) | `12345678` |
| `TELEGRAM_API_HASH` | Telegram API Hash | `abcdef1234...` |
| `TELEGRAM_SESSION` | Назва файлу сесії Telethon (без .session) | `telegram_session` |
| `TELEGRAM_PUBLISH_CHANNEL` | ID або username каналу | `-1001234567890` |
| `OPENAI_API_KEY` | OpenAI API ключ | `sk-...` |

> **Примітка:** Якщо `TELEGRAM_API_ID` або `TELEGRAM_PUBLISH_CHANNEL` порожні — парсинг та публікація в Telegram пропускаються з попередженням у логах.

---

## API-ендпоінти

Повна інтерактивна документація: **http://localhost:8000/docs**

### Sources (Джерела новин)

```http
GET    /api/sources/              # Список усіх джерел
POST   /api/sources/              # Додати джерело
GET    /api/sources/{id}          # Отримати джерело
PATCH  /api/sources/{id}          # Оновити джерело
DELETE /api/sources/{id}          # Видалити джерело
```

**Приклад — додати сайт-джерело:**
```bash
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{"name": "DOU", "type": "site", "url": "https://dou.ua/lenta/", "enabled": true}'
```

**Приклад — додати Telegram-канал:**
```bash
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Tech UA", "type": "tg", "url": "techuachannel", "enabled": true}'
```

### Keywords (Ключові слова для фільтрації)

```http
GET    /api/keywords/             # Список ключових слів
POST   /api/keywords/             # Додати ключове слово
DELETE /api/keywords/{id}         # Видалити ключове слово
```

**Приклад:**
```bash
curl -X POST http://localhost:8000/api/keywords/ \
  -H "Content-Type: application/json" \
  -d '{"word": "штучний інтелект"}'
```

> **Увага:** Якщо ключові слова додані — новини фільтруються. Якщо список порожній — зберігаються всі новини.

### News (Новини)

```http
GET    /api/news/                 # Список новин (від нових до старих)
DELETE /api/news/{id}             # Видалити новину
```

### Posts (Пости)

```http
GET    /api/posts/                # Список усіх постів (від нових до старих)
GET    /api/posts/errors/         # Пости зі статусом "failed"
DELETE /api/posts/{id}            # Видалити пост
```

### Tasks (Ручне керування)

```http
POST   /api/parse/trigger         # Запустити збір новин вручну
POST   /api/generate/             # Згенерувати пост для конкретної новини
```

**Приклад — ручний запуск парсингу:**
```bash
curl -X POST http://localhost:8000/api/parse/trigger
# {"task_id": "abc-123", "status": "queued"}
```

**Приклад — ручна генерація поста:**
```bash
curl -X POST http://localhost:8000/api/generate/ \
  -H "Content-Type: application/json" \
  -d '{"news_id": 1}'
```

---

## Pipeline

```
Celery Beat (кожні 30 хв)
        │
        ▼
parse_sites_task / parse_telegram_task
        │  збирає новини з усіх активних джерел
        ▼
filter_and_store_task
        │  фільтрує за ключовими словами
        │  зберігає нові NewsItem до БД (дублі ігноруються)
        ▼
generate_post_task
        │  генерує пост через OpenAI GPT-4o
        │  зберігає Post зі статусом "generated"
        ▼
publish_telegram_task
        │  публікує пост у Telegram-канал через Telethon
        └  оновлює статус Post → "published"
```

---

## Чек-ліст

- [x] Збір новин із сайтів (Celery Beat, 30 хв)
- [x] Збір новин із Telegram-каналів (Telethon, з graceful fallback)
- [x] Фільтрація та дедуплікація новин
- [x] AI-генерація постів (OpenAI GPT-4o, retry logic)
- [x] Публікація в Telegram (Telethon)
- [x] API Sources (CRUD)
- [x] API Keywords (CRUD)
- [x] API Posts (GET + errors)
- [x] Ручна генерація `/api/generate/`
- [x] Ручний запуск парсингу `/api/parse/trigger`
- [x] Swagger-документація `/docs`
- [x] Логування
- [x] Docker Compose (app, celery_worker, celery_beat, flower, rabbitmq, redis, postgres)
- [x] Flower моніторинг черги
