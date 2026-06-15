import asyncio
import logging
from datetime import timezone

from app.config import settings

logger = logging.getLogger(__name__)

_CREDENTIALS_AVAILABLE = bool(
    settings.TELEGRAM_API_ID and settings.TELEGRAM_API_HASH
)


async def _fetch_channel(channel_username: str, source_name: str, limit: int = 20) -> list[dict]:
    """Async helper: fetch recent messages from a public Telegram channel via Telethon."""
    from telethon import TelegramClient
    from telethon.tl.types import Message

    items = []
    client = TelegramClient(
        settings.TELEGRAM_SESSION,
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
    )
    try:
        await client.start()
        async for message in client.iter_messages(channel_username, limit=limit):
            if not isinstance(message, Message) or not message.text:
                continue
            title = message.text[:100].replace("\n", " ")
            items.append({
                "title": title,
                "url": None,
                "summary": message.text[:500],
                "source": source_name,
                "published_at": message.date.replace(tzinfo=timezone.utc),
                "raw_text": message.text,
            })
    except Exception as e:
        logger.error(f"Error fetching Telegram channel {channel_username}: {e}")
    finally:
        await client.disconnect()
    return items


def parse_telegram_channel(channel_username: str, source_name: str) -> list[dict]:
    """Synchronous wrapper for use inside Celery tasks.

    Returns an empty list if Telegram API credentials are not configured.
    """
    if not _CREDENTIALS_AVAILABLE:
        logger.warning(
            "Telegram parsing skipped: TELEGRAM_API_ID or TELEGRAM_API_HASH not configured"
        )
        return []
    return asyncio.run(_fetch_channel(channel_username, source_name))