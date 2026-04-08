from pathlib import Path

from quant_research_agent.models import AlphaProposal, ArticleSummary, DailyRunReport, ValidationResult
from quant_research_agent.paths import REPORTS_DIR, ensure_project_dirs


def render_daily_markdown(
    run_date: str,
    *,
    status: str,
    collected_count: int,
    fresh_count: int,
    duplicate_count: int,
    selected_count: int,
    generated_alpha_count: int,
    validated_count: int,
    serious_required_count: int,
    serious_available_count: int,
    serious_selected_count: int,
    serious_shortfall: int,
    article_sections: list[dict],
) -> DailyRunReport:
    lines = [
        f"# Quant Research Agent Report - {run_date}",
        "",
        f"- Status: {status}",
        f"- Collected articles: {collected_count}",
        f"- Fresh candidates discovered today: {fresh_count}",
        f"- Duplicates skipped today: {duplicate_count}",
        f"- Selected for research: {selected_count}",
        f"- Generated alphas: {generated_alpha_count}",
        f"- Validated alphas: {validated_count}",
        (
            f"- Serious research quota: {serious_selected_count}/{selected_count} selected, "
            f"target={serious_required_count}, available={serious_available_count}"
        ),
        "",
    ]
    if serious_shortfall:
        lines.extend(
            [
                f"- Serious-source shortfall: {serious_shortfall}",
                "",
            ]
        )
    for section in article_sections:
        lines.append(f"## {section['title']}")
        lines.append("")
        lines.append(f"- Source: {section['source_name']}")
        lines.append(f"- Source type: {section.get('source_class', 'unknown')}")
        lines.append(f"- URL: {section['canonical_url']}")
        lines.append(f"- Theme: {section['summary'].theme}")
        lines.append(f"- Summary: {section['summary'].summary_text}")
        lines.append(f"- Notes: {section['summary'].notes}")
        lines.append("")
        for idea_item in section.get("idea_items", []):
            draft = idea_item["draft"]
            lines.append(f"### Idea Draft: {draft.idea_title}")
            lines.append("")
            lines.append(f"- Source link: {draft.source_link}")
            lines.append(f"- Source type: {draft.source_type}")
            lines.append(f"- Description: {draft.idea_description}")
            lines.append(f"- Signal intuition: {draft.signal_intuition}")
            lines.append(f"- Source annotation: {draft.source_annotation}")
            lines.append(f"- Evidence gap: {draft.evidence_gap}")
            lines.append(f"- Suggested variables: {', '.join(draft.suggested_variables)}")
            lines.append(f"- Suggested operators: {', '.join(draft.suggested_operators)}")
            lines.append(f"- Desired operators: {', '.join(draft.desired_operators)}")
            lines.append(f"- Desired datasets/datafields: {', '.join(draft.desired_datasets_or_datafields)}")
            lines.append(f"- Formula sketch (EN): {draft.formula_sketch_en}")
            lines.append(f"- Why not translated yet: {draft.why_not_translated_yet}")
            lines.append("- Status: awaiting manual expression")
            lines.append("")
        for item in section["alpha_items"]:
            proposal: AlphaProposal = item["proposal"]
            review = item.get("review")
            result: ValidationResult | None = item["result"]
            detail = item.get("detail")
            lines.append(f"### Alpha: `{proposal.expression}`")
            lines.append("")
            if detail is not None:
                lines.append(f"- Source link: {detail.source_link}")
                lines.append(f"- Source type: {detail.source_type}")
                lines.append(f"- Core claim: {detail.core_claim}")
            lines.append(f"- Explanation: {proposal.alpha_explanation}")
            lines.append(f"- Source annotation: {proposal.source_annotation}")
            lines.append(f"- Translation notes: {proposal.translation_notes}")
            if detail is not None and detail.key_source_excerpts:
                lines.append("- Key source excerpts:")
                for excerpt in detail.key_source_excerpts:
                    lines.append(f"  - {excerpt}")
            if detail is not None:
                lines.append(f"- Evidence analysis: {detail.evidence_analysis}")
                lines.append(f"- Translation bridge: {detail.translation_bridge}")
                lines.append(f"- Caveats: {detail.caveats}")
                lines.append(f"- Upgrade directions: {detail.upgrade_directions}")
            lines.append(f"- Critic notes: {review.critic_notes if review else proposal.critic_notes or 'No critic review.'}")
            lines.append(
                f"- Critic status: {'accepted' if review and review.passed_review else 'rejected' if review else 'not reviewed'}"
            )
            if result is None:
                if review and review.passed_review:
                    lines.append("- Validation: pending manual validation (automatic run cap is 3 per daily run)")
                else:
                    lines.append("- Validation: not run")
            else:
                lines.append(
                    f"- Validation: Sharpe={result.sharpe}, Fitness={result.fitness}, Returns={result.returns}, "
                    f"Turnover={result.turnover}, Alpha ID={result.alpha_id}, Error={result.error}"
                )
            lines.append("")

    markdown = "\n".join(lines).strip() + "\n"
    return DailyRunReport(
        run_date=run_date,
        status=status,
        collected_count=collected_count,
        selected_count=selected_count,
        generated_alpha_count=generated_alpha_count,
        validated_count=validated_count,
        markdown=markdown,
    )


def export_daily_markdown(report: DailyRunReport) -> Path:
    ensure_project_dirs()
    output_path = REPORTS_DIR / f"{report.run_date}.md"
    output_path.write_text(report.markdown, encoding="utf-8")
    return output_path
