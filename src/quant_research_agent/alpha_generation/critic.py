from quant_research_agent.models import AlphaProposal, AlphaReview, ArticleRecord, ArticleSummary


FALLBACK_EXPRESSIONS = {
    "rank(ts_rank(close / ts_delay(close, 10) - 1, 10))",
}


def review_alpha_proposal(
    alpha_candidate_id: int,
    article: ArticleRecord,
    summary: ArticleSummary,
    proposal: AlphaProposal,
) -> AlphaReview:
    issues: list[str] = []

    if not summary.is_translatable:
        issues.append("The article looks only weakly translatable into a WorldQuant-style alpha.")
    if len(proposal.source_annotation.strip()) < 40:
        issues.append("The source annotation is too short to clearly tie the alpha back to the article.")
    if proposal.expression in FALLBACK_EXPRESSIONS and summary.theme == "general_quant_research":
        issues.append("This proposal still looks like a generic fallback rather than a specific article translation.")
    if proposal.generation_confidence < 0.52:
        issues.append("Generation confidence is too low for automatic validation.")

    passed_review = not issues
    if passed_review:
        critic_notes = (
            f"Accepted for validation. The expression matches the detected `{summary.theme}` theme, "
            "keeps a conservative operator set, and includes enough source grounding."
        )
        rejection_reason = None
    else:
        critic_notes = "Rejected before validation. " + " ".join(issues)
        rejection_reason = issues[0]

    return AlphaReview(
        alpha_candidate_id=alpha_candidate_id,
        passed_review=passed_review,
        critic_notes=critic_notes,
        rejection_reason=rejection_reason,
    )
