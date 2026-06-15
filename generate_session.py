"""
Utility script to generate a Telegram session file locally before running Docker.
Since Docker runs in the background, it cannot ask you for your phone number and login code.

Usage:
1. Ensure your .env file is filled out with TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_SESSION
2. Run this script locally: `python generate_session.py`
3. Enter your phone number and the code sent to your Telegram app.
4. The script will create a `<session_name>.session` file in this directory.
5. You can now run `docker-compose up -d` and the bot will use this session.
"""
import asyncio
from telethon import TelegramClient
from app.config import settings

async def main():
    print(f"Creating session '{settings.TELEGRAM_SESSION}' using API_ID: {settings.TELEGRAM_API_ID}")
    client = TelegramClient(settings.TELEGRAM_SESSION, settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)
    
    # client.start() automatically prompts for phone and code if not authorized
    await client.start()
    
    me = await client.get_me()
    print(f"\n✅ Successfully authorized as: {me.first_name} {me.last_name or ''} (@{me.username})")
    print(f"✅ Session file '{settings.TELEGRAM_SESSION}.session' has been created/updated.")
    print("You can now start Docker and the bot will publish posts automatically!")

if __name__ == "__main__":
    asyncio.run(main())
