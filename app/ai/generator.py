import logging
import time
from openai import RateLimitError, APIStatusError
from app.ai.openai_client import get_openai_client

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = (
    "Зроби короткий, цікавий опис новини для Telegram-каналу, "
    "додай емодзі (emoji), call to action. "
    "Новина:\n\nЗаголовок: {title}\n\nТекст: {text}"
)

MAX_RETRIES = 3
RETRY_DELAY = 5


def generate_post_text(news) -> str:
    client = get_openai_client()
    prompt = PROMPT_TEMPLATE.format(
        title=news.title,
        text=(news.summary or news.raw_text or "")[:1500],
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.7,
            )
            ai_text = response.choices[0].message.content.strip()
            source_line = f"\nДжерело: {news.url}" if news.url else ""
            generated_text = f"{ai_text}{source_line}"
            logger.info(f"generate_post_text: success for news_id={getattr(news, 'id', '?')}")
            return generated_text

        except RateLimitError as e:
            wait = RETRY_DELAY * attempt
            logger.warning(
                f"OpenAI rate limit hit (attempt {attempt}/{MAX_RETRIES}), retrying in {wait}s: {e}"
            )
            if attempt == MAX_RETRIES:
                raise
            time.sleep(wait)

        except APIStatusError as e:
            logger.error(f"OpenAI API error {e.status_code}: {e.message}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI: {e}")
            raise

    return None