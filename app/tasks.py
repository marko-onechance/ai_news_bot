import logging
from celery_worker import celery_app
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.db import SyncSessionLocal
from app.models import Source, NewsItem, Keyword, Post
from app.news_parser.sites import parse_site
from app.news_parser.telegram import parse_telegram_channel

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.parse_sites_task", bind=True, max_retries=3)
def parse_sites_task(self):
    try:
        with SyncSessionLocal() as db:
            result = db.execute(select(Source).where(Source.type == "site", Source.enabled == True))
            sources = result.scalars().all()

        all_items = []
        for source in sources:
            items = parse_site(source.url, source.name)
            all_items.extend(items)

        if all_items:
            filter_and_store_task.delay(all_items)

        logger.info(f"parse_sites_task: fetched {len(all_items)} items from {len(sources)} sources")
        return {"number_of_items": len(all_items)}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="tasks.parse_telegram_task", bind=True, max_retries=3)
def parse_telegram_task(self):
    try:
        with SyncSessionLocal() as db:
            result = db.execute(select(Source).where(Source.type == "tg", Source.enabled == True))
            sources = result.scalars().all()

        all_items = []
        for source in sources:
            items = parse_telegram_channel(source.url, source.name)
            all_items.extend(items)

        if all_items:
            filter_and_store_task.delay(all_items)

        logger.info(f"parse_telegram_task: fetched {len(all_items)} items from {len(sources)} sources")
        return {"number_of_items": len(all_items)}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="tasks.filter_and_store_task")
def filter_and_store_task(items: list):
    with SyncSessionLocal() as db:
        kw_result = db.execute(select(Keyword))
        keywords = [k.word.lower() for k in kw_result.scalars().all()]

    saved_ids = []
    for item in items:
        if keywords:
            text = (
                f"{item.get('title', '')} "
                f"{item.get('summary', '')} "
                f"{item.get('raw_text', '')}"
            ).lower()
            if not any(kw in text for kw in keywords):
                continue
        with SyncSessionLocal() as db:
            news = NewsItem(**item)
            db.add(news)
            try:
                db.commit()
                db.refresh(news)
                saved_ids.append(news.id)
            except IntegrityError:
                db.rollback()

    logger.info(f"filter_and_store_task: stored {len(saved_ids)} new news items")
    for news_id in saved_ids:
        generate_post_task.delay(news_id)


@celery_app.task(name="tasks.generate_post_task", bind=True, max_retries=2)
def generate_post_task(self, news_id: int):
    from app.ai.generator import generate_post_text
    with SyncSessionLocal() as db:
        news = db.get(NewsItem, news_id)
        if not news:
            return None
        try:
            generated_text = generate_post_text(news)
        except Exception as exc:
            post = Post(news_id=news_id, generated_text="", status="failed")
            db.add(post)
            db.commit()
            raise self.retry(exc=exc, countdown=120)

        post = Post(news_id=news_id, generated_text=generated_text, status="generated")
        db.add(post)
        db.commit()
        db.refresh(post)

    if post.id:
        publish_telegram_task.delay(post.id)
        return post.id
    return False


@celery_app.task(name="tasks.publish_telegram_task", bind=True, max_retries=3)
def publish_telegram_task(self, post_id: int):
    from app.telegram.publisher import publish_post
    from datetime import datetime, timezone
    with SyncSessionLocal() as db:
        post = db.get(Post, post_id)
        if not post or post.status == "published":
            return
        try:
            publish_post(post.generated_text)
            post.status = "published"
            post.published_at = datetime.now(timezone.utc)
            db.commit()
        except Exception as exc:
            post.status = "failed"
            db.commit()
            raise self.retry(exc=exc, countdown=60)