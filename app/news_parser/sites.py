import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


def parse_site(url: str, source_name: str) -> list[dict]:
    items = []
    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        articles = soup.find_all("article")
        if not articles:
            articles = soup.find_all("div", class_=lambda c: c and "news" in c.lower())

        for article in articles[:5]:
            title_tag = article.find(["h1", "h2", "h3", "a"])
            title = title_tag.get_text(strip=True) if title_tag else None
            if not title:
                continue

            link_tag = article.find("a", href=True)
            article_url = link_tag["href"] if link_tag else None
            if article_url and article_url.startswith("/"):
                article_url = urljoin(url, article_url)

            paragraphs = article.find_all("p")
            raw_text = " ".join(p.get_text(strip=True) for p in paragraphs)
            summary = raw_text[:500] if raw_text else title

            items.append({
                "title": title,
                "url": article_url,
                "summary": summary,
                "source": source_name,
                "published_at": datetime.now(timezone.utc),
                "raw_text": raw_text,
            })

    except Exception as e:
        logger.error(f"Error parsing site {url}: {e}")

    return items