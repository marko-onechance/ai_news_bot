![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136.3-009688?logo=fastapi&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.6.3-37814A?logo=celery&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.13-FF6600?logo=rabbitmq&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-2.41.1-412991?logo=openai&logoColor=white)
![Telethon](https://img.shields.io/badge/Telethon-1.43.2-2CA5E0?logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

# AI News Bot for Telegram

**English** · [Українська](README.uk.md)

A service that collects news from websites and public Telegram channels, filters and deduplicates them, generates vivid posts using OpenAI GPT-4o, and publishes them to a Telegram channel — all driven by a REST API with Swagger documentation.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Pipeline](#pipeline)
- [Checklist](#checklist)

---

## Features

| # | Feature | Technology |
|---|---------|-----------|
| 1 | News collection from websites | Celery Beat, requests, BeautifulSoup |
| 2 | News collection from Telegram channels | Celery Beat, Telethon |
| 3 | Keyword-based filtering | Python, PostgreSQL |
| 4 | News deduplication | PostgreSQL UNIQUE constraints |
| 5 | AI post generation | OpenAI GPT-4o |
| 6 | Telegram publishing | Telethon |
| 7 | REST API (CRUD for sources & keywords) | FastAPI |
| 8 | Post history & error log endpoints | FastAPI |
| 9 | Manual post generation via API | FastAPI + OpenAI |
| 10 | Swagger documentation | FastAPI `/docs` |
| 11 | Task queue monitoring | Celery Flower |

---

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings (pydantic-settings)
│   ├── db.py                # Async + Sync SQLAlchemy engines
│   ├── models.py            # ORM models: Source, NewsItem, Keyword, Post
│   ├── tasks.py             # Celery tasks pipeline
│   ├── utils.py             # Logging setup
│   ├── api/
│   │   ├── endpoints.py     # FastAPI routers
│   │   └── schemas.py       # Pydantic schemas
│   ├── ai/
│   │   ├── openai_client.py # OpenAI client singleton
│   │   └── generator.py     # Post generation with retry logic
│   ├── news_parser/
│   │   ├── sites.py         # HTML site parser (BeautifulSoup)
│   │   └── telegram.py      # Telegram channel parser (Telethon)
│   └── telegram/
│       └── publisher.py     # Telegram publisher (Telethon)
├── celery_worker.py         # Celery app + Beat schedule
├── docker-compose.yml       # Full infrastructure
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Getting Started

### 1. Clone the repository and configure `.env`

```bash
git clone <repo-url>
cd 1_ai_new_bot
cp .env.example .env
# Edit .env — fill in your OpenAI and Telegram credentials
```

### 2. Authenticate with Telegram (Required for publishing)

Since Docker runs in the background, you must generate a Telegram session file locally first so Telethon can authorize without interactive prompts.

```bash
# Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate
pip install telethon python-dotenv

# Run the interactive login script
python generate_session.py
```
*Enter your phone number and the login code from Telegram. This will generate a `.session` file matching your `TELEGRAM_SESSION` variable.*

### 3. Start all services with Docker Compose

```bash
docker-compose up --build
```

This will start:
- **FastAPI** → http://localhost:8000
- **Swagger UI** → http://localhost:8000/docs
- **RabbitMQ Management** → http://localhost:15672 (guest/guest)
- **Celery Flower** → http://localhost:5555
- **PostgreSQL** → localhost:5432
- **Redis** → localhost:6379

### 4. (Optional) Local run without Docker

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL, RabbitMQ and Redis separately, then:
uvicorn app.main:app --reload --port 8000 &
celery -A celery_worker.celery_app worker --loglevel=info &
celery -A celery_worker.celery_app beat --loglevel=info
```

---

## Environment Variables

Copy `.env.example` → `.env` and fill in the values:

| Variable | Description | Example |
|----------|-------------|---------|
| `PG_USERNAME` | PostgreSQL user | `ainewsbot` |
| `PG_PASSWORD` | PostgreSQL password | `postgres` |
| `PG_HOST` | PostgreSQL host | `postgres` (Docker) / `localhost` |
| `PG_NAME` | PostgreSQL database name | `ainewsbot` |
| `RABBITMQ_URL` | RabbitMQ broker URL | `amqp://guest:guest@rabbitmq:5672//` |
| `REDIS_URL` | Redis URL (Celery backend) | `redis://redis:6379/0` |
| `TELEGRAM_API_ID` | Telegram API ID (my.telegram.org) | `12345678` |
| `TELEGRAM_API_HASH` | Telegram API Hash | `abcdef1234...` |
| `TELEGRAM_SESSION` | Telethon session file name (without .session) | `telegram_session` |
| `TELEGRAM_PUBLISH_CHANNEL` | Channel ID or username | `-1001234567890` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |

> **Note:** If `TELEGRAM_API_ID` or `TELEGRAM_PUBLISH_CHANNEL` are empty, Telegram parsing and publishing are skipped with a warning in the logs.

---

## API Endpoints

Full interactive documentation: **http://localhost:8000/docs**

### Sources

```http
GET    /api/sources/              # List all sources
POST   /api/sources/              # Add a source
GET    /api/sources/{id}          # Get a source
PATCH  /api/sources/{id}          # Update a source
DELETE /api/sources/{id}          # Delete a source
```

**Example — add a website source:**
```bash
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{"name": "DOU", "type": "site", "url": "https://dou.ua/lenta/", "enabled": true}'
```

**Example — add a Telegram channel:**
```bash
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Tech UA", "type": "tg", "url": "techuachannel", "enabled": true}'
```

### Keywords

```http
GET    /api/keywords/             # List keywords
POST   /api/keywords/             # Add a keyword
DELETE /api/keywords/{id}         # Delete a keyword
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/keywords/ \
  -H "Content-Type: application/json" \
  -d '{"word": "artificial intelligence"}'
```

> **Note:** If keywords are set, only matching news is saved. If the list is empty, all news is stored.

### News

```http
GET    /api/news/                 # List news (newest first)
DELETE /api/news/{id}             # Delete a news item
```

### Posts

```http
GET    /api/posts/                # List all posts (newest first)
GET    /api/posts/errors/         # Posts with status "failed"
DELETE /api/posts/{id}            # Delete a post
```

### Tasks

```http
POST   /api/parse/trigger         # Manually trigger news collection
POST   /api/generate/             # Manually generate a post for a news item
```

**Example — trigger parsing manually:**
```bash
curl -X POST http://localhost:8000/api/parse/trigger
# {"task_id": "abc-123", "status": "queued"}
```

**Example — manually generate a post:**
```bash
curl -X POST http://localhost:8000/api/generate/ \
  -H "Content-Type: application/json" \
  -d '{"news_id": 1}'
```

---

## Pipeline

```
Celery Beat (every 30 min)
        │
        ▼
parse_sites_task / parse_telegram_task
        │  collects news from all enabled sources
        ▼
filter_and_store_task
        │  filters by keywords
        │  saves new NewsItems to DB (duplicates skipped)
        ▼
generate_post_task
        │  generates post via OpenAI GPT-4o
        │  saves Post with status "generated"
        ▼
publish_telegram_task
        │  publishes post to Telegram channel via Telethon
        └  updates Post status → "published"
```

---

## Checklist

- [x] News collection from websites (Celery Beat, every 30 min)
- [x] News collection from Telegram channels (Telethon, with graceful fallback)
- [x] Keyword filtering and deduplication
- [x] AI post generation (OpenAI GPT-4o, retry logic)
- [x] Telegram publishing (Telethon)
- [x] API Sources (CRUD)
- [x] API Keywords (CRUD)
- [x] API Posts (GET + errors)
- [x] Manual generation `/api/generate/`
- [x] Manual parse trigger `/api/parse/trigger`
- [x] Swagger documentation `/docs`
- [x] Logging
- [x] Docker Compose (app, celery_worker, celery_beat, flower, rabbitmq, redis, postgres)
- [x] Celery Flower monitoring
