import math
import math
from collections import Counter
from dataclasses import dataclass

from quant_research_agent.models import ArticleRecord


KEYWORD_WEIGHTS = {
    "alpha": 4,
    "factor": 4,
    "portfolio": 2,
    "anomaly": 3,
    "volatility": 2,
    "momentum": 3,
    "liquidity": 2,
    "cross-sectional": 4,
    "return": 1,
    "signal": 2,
    "pricing": 2,
    "microstructure": 3,
}

TRANSLATABLE_MARKERS = {
    "price": 2,
    "close": 2,
    "volume": 2,
    "return": 2,
    "spread": 2,
    "earnings": 1,
    "volatility": 2,
    "turnover": 2,
    "vwap": 2,
}

SERIOUS_SOURCE_CLASSES = {"research_paper", "research_report"}


@dataclass
class RankedArticle:
    article: ArticleRecord
    score: float
    reasons: list[str]


def score_article(article: ArticleRecord, *, update_penalty: float = 0.0, novelty_penalty: float = 0.0) -> RankedArticle:
    text = f"{article.title} {article.extracted_text[:3000]}".lower()
    keyword_score = sum(weight for keyword, weight in KEYWORD_WEIGHTS.items() if keyword in text)
    variable_score = sum(weight for keyword, weight in TRANSLATABLE_MARKERS.items() if keyword in text)
    length_score = min(len(article.extracted_text) / 1800, 4.0)
    source_score = article.source_priority * 2.8
    total = source_score + keyword_score + variable_score + length_score - update_penalty - novelty_penalty

    reasons = [
        f"source_class={article.source_class}",
        f"source={article.source_priority}",
        f"keywords={keyword_score}",
        f"translatable={variable_score}",
        f"length={length_score:.1f}",
    ]
    if update_penalty:
        reasons.append(f"update_penalty={update_penalty:.1f}")
    if novelty_penalty:
        reasons.append(f"novelty_penalty={novelty_penalty:.1f}")
    return RankedArticle(article=article, score=round(total, 2), reasons=reasons)


def rank_article_items(items: list[dict], limit: int = 10) -> dict:
    token_counts = Counter()
    for item in items:
        title_tokens = {token for token in item["article"].title.lower().split() if len(token) > 3}
        token_counts.update(title_tokens)

    ranked_payloads = []
    for item in items:
        article = item["article"]
        title_tokens = {token for token in article.title.lower().split() if len(token) > 3}
        overlap_penalty = max(sum(max(token_counts[token] - 1, 0) for token in title_tokens) * 0.2, 0.0)
        update_penalty = 1.2 if item.get("action") == "updated" else 0.0
        ranked = score_article(article, update_penalty=update_penalty, novelty_penalty=overlap_penalty)
        ranked_payloads.append(
            {
                "article": article,
                "article_id": item["article_id"],
                "action": item["action"],
                "score": ranked.score,
                "reasons": ranked.reasons,
            }
        )

    ranked_payloads.sort(key=lambda item: item["score"], reverse=True)
    serious_required = math.ceil(limit / 2)
    serious_candidates = [
        item for item in ranked_payloads
        if item["article"].source_class in SERIOUS_SOURCE_CLASSES
    ]
    selected: list[dict] = []
    selected_ids: set[int] = set()

    for item in serious_candidates[:serious_required]:
        selected.append(item)
        selected_ids.add(int(item["article_id"]))

    for item in ranked_payloads:
        if len(selected) >= limit:
            break
        if int(item["article_id"]) in selected_ids:
            continue
        selected.append(item)
        selected_ids.add(int(item["article_id"]))

    serious_selected = sum(
        1 for item in selected
        if item["article"].source_class in SERIOUS_SOURCE_CLASSES
    )
    return {
        "selected_items": selected[:limit],
        "serious_required_count": serious_required,
        "serious_selected_count": serious_selected,
        "serious_available_count": len(serious_candidates),
        "serious_shortfall": max(0, serious_required - serious_selected),
    }


def rank_articles(articles: list[ArticleRecord], limit: int = 10) -> list[ArticleRecord]:
    scored = [score_article(article) for article in articles]
    scored.sort(key=lambda item: item.score, reverse=True)
    return [item.article for item in scored[:limit]]


def describe_article_mix(articles: list[ArticleRecord]) -> str:
    source_counts = Counter(article.source_name for article in articles)
    class_counts = Counter(article.source_class for article in articles)
    source_part = ", ".join(f"{name}:{count}" for name, count in source_counts.items())
    class_part = ", ".join(f"{name}:{count}" for name, count in class_counts.items())
    if source_part and class_part:
        return f"sources[{source_part}] classes[{class_part}]"
    return source_part or class_part
