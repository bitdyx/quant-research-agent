from typing import Any

from quant_research_agent.knowledge.service import SERIOUS_SOURCE_CLASSES, build_source_evidence_context
from quant_research_agent.models import AlphaProposal, ArticleRecord, ArticleSummary


ALPHA_LIBRARY = {
    "momentum": [
        (
            "rank(ts_rank(close / ts_delay(close, 20) - 1, 10))",
            "This alpha keeps the article's momentum intuition by ranking medium-horizon price continuation.",
        ),
        (
            "rank(ts_rank(close / vwap - 1, 10))",
            "This alpha conservatively maps the article's price-strength idea into a close-versus-vwap ranking.",
        ),
    ],
    "mean_reversion": [
        (
            "rank(-ts_delta(close, 5))",
            "This alpha expresses short-horizon reversal by preferring names with recent negative price change.",
        ),
        (
            "rank(-(close / ts_mean(close, 20) - 1))",
            "This alpha captures mean reversion by penalizing names trading far above their recent average.",
        ),
    ],
    "volatility": [
        (
            "rank(-ts_std_dev(close / ts_delay(close, 1) - 1, 20))",
            "This alpha follows the article's risk intuition by favoring stocks with calmer recent return dispersion.",
        ),
    ],
    "liquidity": [
        (
            "rank(ts_rank(volume / adv20, 20))",
            "This alpha translates the article's liquidity signal into a ranked recent volume pressure measure.",
        ),
        (
            "rank(ts_rank((close - vwap) * (volume / adv20), 20))",
            "This alpha conservatively mixes volume pressure with intraday price positioning.",
        ),
    ],
    "quality": [
        (
            "rank(-ts_std_dev(close / ts_delay(close, 1) - 1, 20))",
            "This first-pass proxy keeps the article's quality intuition by rewarding names with steadier short-term behavior.",
        ),
    ],
    "value": [
        (
            "rank(-(close / ts_mean(close, 66) - 1))",
            "This alpha conservatively approximates value by preferring names that remain cheap versus their medium-term baseline.",
        ),
    ],
    "general_quant_research": [
        (
            "rank(ts_rank(close / ts_delay(close, 10) - 1, 10))",
            "This fallback alpha keeps the translation conservative by using a simple, broadly available price-strength signal.",
        ),
    ],
}


def _supporting_excerpt(article: ArticleRecord, summary: ArticleSummary, theme: str) -> str:
    evidence = build_source_evidence_context(article, summary)
    if evidence["key_source_excerpts"]:
        return " | ".join(evidence["key_source_excerpts"][:2])[:400]
    lowered_theme = theme.replace("_", " ")
    sentences = article.extracted_text.split(". ")
    for sentence in sentences:
        if lowered_theme.split()[0] in sentence.lower():
            return sentence.strip()[:400]
    return summary.summary_text[:400]


def _knowledge_templates(knowledge_context: dict[str, list[dict[str, Any]]] | None) -> list[tuple[str, str, str]]:
    if not knowledge_context:
        return []
    templates: list[tuple[str, str, str]] = []
    seen_expressions: set[str] = set()

    for row in knowledge_context.get("memory_alpha_examples", []):
        expression = (row.get("expression") or "").strip()
        if not expression or expression in seen_expressions:
            continue
        seen_expressions.add(expression)
        explanation = (
            f"This proposal starts from a remembered alpha linked to similar prior research: "
            f"{row.get('alpha_explanation') or 'a previously remembered local alpha'}"
        )
        translation_notes = (
            "The expression was seeded from a remembered alpha that you previously marked as important, "
            "so the agent is reusing your local research memory before falling back to generic templates."
        )
        templates.append((expression, explanation, translation_notes))

    for row in knowledge_context.get("datafield_examples", []):
        expression = (row.get("example_expression") or "").strip()
        if not expression or expression in seen_expressions:
            continue
        seen_expressions.add(expression)
        field_id = row.get("field_id", "unknown_field")
        vector_handling = row.get("vector_handling", "none")
        explanation = (
            f"This proposal reuses confirmed local knowledge about datafield '{field_id}'"
            f" and keeps the translation conservative."
        )
        translation_notes = (
            f"The expression was seeded from confirmed local datafield knowledge. "
            f"Detected vector handling: {vector_handling}."
        )
        templates.append((expression, explanation, translation_notes))

    for row in knowledge_context.get("operator_examples", []):
        expression = (row.get("example_expression") or "").strip()
        if not expression or expression in seen_expressions:
            continue
        seen_expressions.add(expression)
        operator_name = row.get("name", "unknown_operator")
        explanation = (
            f"This proposal starts from confirmed local operator knowledge for '{operator_name}'"
            f" instead of relying only on the generic fallback library."
        )
        translation_notes = (
            "The expression was seeded from confirmed operator knowledge already stored in the local "
            "WorldQuant knowledge base."
        )
        templates.append((expression, explanation, translation_notes))

    return templates


def generate_alpha_proposals(
    article_id: int,
    article: ArticleRecord,
    summary: ArticleSummary,
    knowledge_context: dict[str, list[dict[str, Any]]] | None = None,
    max_alphas: int = 3,
) -> list[AlphaProposal]:
    knowledge_templates = _knowledge_templates(knowledge_context)
    if not summary.is_translatable and not knowledge_templates:
        return []

    evidence = build_source_evidence_context(article, summary)
    generic_templates: list[tuple[str, str, str | None]] = []
    if evidence["has_sufficient_evidence"] and (
        article.source_class in SERIOUS_SOURCE_CLASSES or knowledge_templates
    ):
        templates = ALPHA_LIBRARY.get(summary.theme, ALPHA_LIBRARY["general_quant_research"])
        generic_templates = [
            (expression, explanation, None) for expression, explanation in templates
        ]

    combined_templates = knowledge_templates + generic_templates
    if not combined_templates:
        return []

    proposals: list[AlphaProposal] = []
    seen_expressions: set[str] = set()
    for rank, (expression, explanation, translation_notes_override) in enumerate(combined_templates, start=1):
        if expression in seen_expressions:
            continue
        seen_expressions.add(expression)
        confidence = max(0.45, 0.84 - rank * 0.1)
        if not summary.is_translatable:
            confidence = min(confidence, 0.5)
        proposals.append(
            AlphaProposal(
                article_id=article_id,
                expression=expression,
                alpha_explanation=explanation,
                source_annotation=_supporting_excerpt(article, summary, summary.theme),
                translation_notes=translation_notes_override
                or (
                    "This first version keeps the translation conservative by mapping the article's core idea "
                    "into broadly available WorldQuant price/volume operators instead of aggressive field-specific engineering."
                ),
                generation_confidence=confidence,
                critic_notes=None,
                conservative_generation=True,
            )
        )
        if len(proposals) >= max_alphas:
            break
    return proposals
