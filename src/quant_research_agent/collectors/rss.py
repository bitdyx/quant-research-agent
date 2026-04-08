import json
import re
from dataclasses import dataclass
from html import unescape
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

from quant_research_agent.models import ArticleRecord
from quant_research_agent.paths import SOURCES_PATH


@dataclass
class SourceConfig:
    name: str
    kind: str
    url: str
    priority: int
    source_class: str


def infer_source_class(name: str, url: str = "") -> str:
    lowered_name = (name or "").lower()
    lowered_url = (url or "").lower()
    if "arxiv" in lowered_name or "ssrn" in lowered_name or "nber" in lowered_name:
        return "research_paper"
    if any(marker in lowered_name for marker in ("research", "whitepaper", "strategy", "report")):
        return "research_report"
    if "quantocracy" in lowered_name or "quantocracy" in lowered_url:
        return "aggregator"
    return "quant_blog"


def load_source_configs(path=SOURCES_PATH) -> list[SourceConfig]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [
        SourceConfig(
            name=item["name"],
            kind=item["kind"],
            url=item["url"],
            priority=item["priority"],
            source_class=item.get("source_class") or infer_source_class(item["name"], item["url"]),
        )
        for item in payload
    ]


def _strip_html(text: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _safe_get_text(parent, tag_names: list[str]) -> str:
    for tag_name in tag_names:
        node = parent.find(tag_name)
        if node is not None and node.text:
            return node.text.strip()
    return ""


class RSSCollector:
    def __init__(self, timeout: int = 20):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
                )
            }
        )

    def fetch(self, max_per_source: int = 20) -> list[ArticleRecord]:
        articles: list[ArticleRecord] = []
        for source in load_source_configs():
            if source.kind != "rss":
                continue
            feed = feedparser.parse(source.url)
            if getattr(feed, "bozo", False) and not getattr(feed, "entries", None):
                continue
            for item in feed.entries[:max_per_source]:
                title = (item.get("title") or "").strip()
                link = (item.get("link") or "").strip()
                description = (item.get("summary") or item.get("description") or "").strip()
                guid = (item.get("id") or item.get("guid") or link).strip()
                published_at = (item.get("published") or item.get("updated") or "").strip()

                if not title or not link:
                    continue

                article_text = self._fetch_article_text(link, fallback=description)
                articles.append(
                    ArticleRecord(
                        source_name=source.name,
                        source_kind=source.kind,
                        source_url=source.url,
                        source_priority=source.priority,
                        source_class=source.source_class,
                        title=title,
                        canonical_url=link,
                        external_id=guid or link,
                        published_at=published_at or None,
                        raw_content=_strip_html(description or article_text),
                        extracted_text=article_text,
                        metadata={
                            "host": urlparse(link).netloc,
                            "collector": "rss",
                            "feed_title": getattr(feed.feed, "title", source.name),
                            "tags": [tag.get("term") for tag in item.get("tags", []) if tag.get("term")],
                        },
                    )
                )
        return articles

    def _fetch_article_text(self, url: str, fallback: str) -> str:
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for node in soup(["script", "style", "noscript"]):
                node.decompose()

            article_node = soup.find("article") or soup.find("main") or soup.body
            text = article_node.get_text(" ", strip=True) if article_node else soup.get_text(" ", strip=True)
            text = re.sub(r"\s+", " ", text).strip()
            cleaned = text[:12000]
            return cleaned if cleaned else _strip_html(fallback)
        except requests.RequestException:
            return _strip_html(fallback)
