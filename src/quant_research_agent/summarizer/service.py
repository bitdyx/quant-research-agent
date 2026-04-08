import re

from quant_research_agent.models import ArticleRecord, ArticleSummary


THEME_KEYWORDS = {
    "momentum": ["momentum", "trend", "relative strength"],
    "mean_reversion": ["mean reversion", "reversal", "overreaction"],
    "volatility": ["volatility", "variance", "risk"],
    "liquidity": ["liquidity", "volume", "turnover", "adv20"],
    "quality": ["quality", "profitability", "cash flow", "earnings quality"],
    "value": ["value", "valuation", "cheap", "book-to-market"],
}


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if len(part.strip()) > 30]


def _detect_theme(text: str) -> str:
    lowered = text.lower()
    scores = []
    for theme, keywords in THEME_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in lowered)
        if score:
            scores.append((score, theme))
    if not scores:
        return "general_quant_research"
    scores.sort(reverse=True)
    return scores[0][1]


def _extract_variables(text: str) -> list[str]:
    mappings = {
        "close": ["close", "price"],
        "volume": ["volume", "turnover"],
        "vwap": ["vwap"],
        "volatility": ["volatility", "variance"],
        "momentum": ["momentum", "trend"],
        "quality": ["profitability", "quality", "cash flow", "earnings"],
    }
    lowered = text.lower()
    variables = [label for label, keywords in mappings.items() if any(keyword in lowered for keyword in keywords)]
    return variables or ["close", "volume"]


def _detect_translatability(text: str) -> tuple[bool, str]:
    lowered = text.lower()
    positive_markers = [
        "cross-sectional",
        "signal",
        "factor",
        "return",
        "momentum",
        "volume",
        "liquidity",
        "volatility",
        "pricing",
    ]
    score = sum(1 for marker in positive_markers if marker in lowered)
    if score >= 2:
        return True, "The article describes signals that can be translated into broadly available price/volume/factor operators."
    return False, "The article looks more conceptual than directly mappable into a WorldQuant-style signal."


def _detect_size_profile(text: str) -> tuple[str | None, str | None]:
    lowered = text.lower()
    if any(marker in lowered for marker in ["mega-cap", "megacap", "blue chip", "largest companies"]):
        return "large_cap", "TOP500"
    if any(marker in lowered for marker in ["large-cap", "large cap", "large capitalization", "market leaders"]):
        return "large_cap", "TOP1000"
    return None, None


def _detect_daily_signal(text: str) -> bool:
    lowered = text.lower()
    markers = ["daily", "next-day", "next day", "one-day", "day-ahead", "daily rebalance"]
    return any(marker in lowered for marker in markers)


def summarize_article(article_id: int, article: ArticleRecord) -> ArticleSummary:
    sentences = _split_sentences(article.extracted_text)
    summary_sentences = sentences[:3] if sentences else [article.title]
    summary_text = " ".join(summary_sentences)[:1200]
    theme = _detect_theme(f"{article.title}. {article.extracted_text}")
    variables = _extract_variables(article.extracted_text)
    size_tilt, suggested_universe = _detect_size_profile(article.extracted_text)
    is_daily_signal = _detect_daily_signal(article.extracted_text)
    is_translatable, translatability_note = _detect_translatability(article.extracted_text)
    market_background = summary_sentences[0] if summary_sentences else article.title

    return ArticleSummary(
        article_id=article_id,
        theme=theme,
        summary_text=summary_text,
        variables=variables,
        frequency="daily" if is_daily_signal else "mixed_or_unspecified",
        market_background=market_background,
        size_tilt=size_tilt,
        suggested_universe=suggested_universe,
        is_daily_signal=is_daily_signal,
        is_translatable=is_translatable,
        notes=(
            f"Conservative heuristic summary generated from article text. {translatability_note} "
            f"Detected variables: {', '.join(variables)}."
        ),
    )
