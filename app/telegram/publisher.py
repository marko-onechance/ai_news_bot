import asyncio
import logging
from telethon import TelegramClient
from app.config import settings

logger = logging.getLogger(__name__)


async def _send_message(text: str):
    client = TelegramClient(
        settings.TELEGRAM_SESSION,
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
    )
    await client.start()
    logger.info("Telethon client started")
    try:
        await client.send_message(settings.TELEGRAM_PUBLISH_CHANNEL, text)
        logger.info(f"Published message to {settings.TELEGRAM_PUBLISH_CHANNEL}")
    finally:
        await client.disconnect()


def publish_post(text: str) -> None:
    """Publish a text message to the configured Telegram channel.

    Uses Telethon under the hood. Skips silently if credentials are not configured.
    This is a synchronous function — safe to call from Celery tasks and FastAPI endpoints.
    """
    logger.info(
        f"publish_post called: API_ID={settings.TELEGRAM_API_ID!r}, "
        f"CHANNEL={settings.TELEGRAM_PUBLISH_CHANNEL!r}"
    )
    if not settings.TELEGRAM_API_ID or not settings.TELEGRAM_PUBLISH_CHANNEL:
        logger.warning("Telegram publishing skipped: credentials not configured")
        return
    asyncio.run(_send_message(text))