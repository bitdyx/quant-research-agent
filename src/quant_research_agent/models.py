from dataclasses import dataclass, field
from typing import Any


@dataclass
class ArticleRecord:
    source_name: str
    source_kind: str
    source_url: str
    source_priority: int
    source_class: str
    title: str
    canonical_url: str
    external_id: str | None
    published_at: str | None
    raw_content: str
    extracted_text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ArticleSummary:
    article_id: int
    theme: str
    summary_text: str
    variables: list[str]
    frequency: str
    market_background: str
    size_tilt: str | None
    suggested_universe: str | None
    is_daily_signal: bool
    is_translatable: bool
    notes: str


@dataclass
class AlphaProposal:
    article_id: int
    expression: str
    alpha_explanation: str
    source_annotation: str
    translation_notes: str
    generation_confidence: float
    critic_notes: str | None = None
    conservative_generation: bool = True


@dataclass
class ValidationSettings:
    region: str = "USA"
    delay: int = 1
    universe: str = "TOP3000"
    neutralization: str = "SUBINDUSTRY"
    decay: int = 4
    truncation: float = 0.08
    settings_reason: str = "default baseline"


@dataclass
class ValidationResult:
    alpha_candidate_id: int
    expression: str
    settings: ValidationSettings
    sharpe: float | None
    fitness: float | None
    returns: float | None
    turnover: float | None
    alpha_id: str | None
    error: str | None


@dataclass
class AlphaReview:
    alpha_candidate_id: int
    passed_review: bool
    critic_notes: str
    rejection_reason: str | None = None


@dataclass
class OperatorKnowledge:
    name: str
    parameter_signature: str
    description: str
    usage_scenarios: str
    common_combinations: str
    example_expression: str
    source: str
    category: str = "Uncategorized"
    is_seeded: bool = False
    last_updated_at: str | None = None


@dataclass
class DatasetKnowledge:
    name: str
    description: str
    source: str


@dataclass
class DatafieldKnowledge:
    field_id: str
    dataset_name: str | None
    field_type: str
    description: str
    use_cases: str
    vector_handling: str
    example_expression: str
    source: str


@dataclass
class IdeaDraft:
    article_id: int
    idea_title: str
    idea_description: str
    source_annotation: str
    suggested_variables: list[str]
    suggested_operators: list[str]
    source_link: str = ""
    source_type: str = ""
    signal_intuition: str = ""
    desired_operators: list[str] = field(default_factory=list)
    desired_datasets_or_datafields: list[str] = field(default_factory=list)
    formula_sketch_en: str = ""
    why_not_translated_yet: str = ""
    evidence_gap: str = ""
    status: str = "awaiting_expression"
    is_memory: bool = False


@dataclass
class IdeaExpression:
    idea_draft_id: int
    expression: str
    submitted_by: str
    submitted_at: str | None = None
    validation_status: str = "submitted"
    validation_error: str | None = None
    alpha_candidate_id: int | None = None


@dataclass
class KnowledgeReviewItem:
    item_type: str
    raw_name: str
    source_expression: str
    source_idea_id: int | None
    source_article_id: int | None
    proposed_description: str
    payload_json: dict[str, Any]
    review_status: str = "pending"


@dataclass
class DailyRunReport:
    run_date: str
    status: str
    collected_count: int
    selected_count: int
    generated_alpha_count: int
    validated_count: int
    markdown: str


@dataclass
class AlphaDetail:
    alpha_candidate_id: int
    source_link: str
    source_type: str
    core_claim: str
    key_source_excerpts: list[str]
    source_analysis: str
    evidence_analysis: str
    translation_bridge: str
    caveats: str
    upgrade_directions: str


@dataclass
class ResearchState:
    run_id: int | None
    run_date: str
    status: str
    current_stage: str
    current_article: str | None
    collected_count: int
    selected_count: int
    generated_alpha_count: int
    validated_count: int
    error: str | None = None
    logs: list[str] = field(default_factory=list)
    started_at: str | None = None
    finished_at: str | None = None
