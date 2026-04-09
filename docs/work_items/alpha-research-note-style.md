# Work Item: Alpha Research Note Style

## GitHub issue title

`Upgrade alpha detail into paper-style replication cards`

## Labels

- `research`
- `pipeline`
- `ui`

## Goal

Upgrade alpha detail from a short explanation block into a real research note that can help you improve expressions by hand.

## Problem statement

The current detail cards are still too shallow:

- evidence analysis is often generic
- translation notes do not clearly show what was mapped from the source article
- caveats are not strong enough to explain what is still missing
- weak-evidence articles can still look more final than they really are

## Required implementation

### 1. Strengthen detail schema

Extend alpha detail so it can hold structured research-note fields:

- `research_question`
- `alpha_hypothesis_cn`
- `evidence_strength`
- `variable_mapping_json`
- `expression_breakdown_json`
- `caveat_items_json`
- `upgrade_checklist_json`

### 2. Strengthen evidence gate

Only generate a formal alpha when:

- the source has enough usable excerpts
- the signal has operator support
- the signal has dataset/datafield support
- the source is not just a weak aggregator-style mention

If any of those conditions fail, route the result to `Idea Inbox` only.

### 3. Upgrade detail rendering

Render detail in this order:

1. source name, type, and link
2. research question
3. core claim
4. 2-4 key source excerpts
5. evidence analysis
6. variable mapping table
7. expression breakdown
8. caveats
9. upgrade checklist

### 4. Keep history compatible

- historical alpha detail should lazily backfill when opened
- existing `Memory`, `Idea Inbox`, and `Knowledge Base` behavior must not regress

## Acceptance criteria

- strong-evidence items render as structured research notes, not summary prose
- weak-evidence items no longer appear as formal alpha cards
- every formal alpha detail includes at least two usable source excerpts
- `Evidence Analysis`, `Translation Bridge`, and `Caveats` become actionable for manual alpha improvement

## Suggested branch

`codex/alpha-research-note-style`

## Draft PR title

`Draft: upgrade alpha detail into paper-style replication cards`

## Draft PR body

### What changed

- upgraded alpha detail into a research-note style schema and UI
- tightened evidence thresholds before a formal alpha can be shown
- routed weak-evidence items to Idea Inbox
- preserved lazy backfill for historical alpha detail

### Why

The previous detail view was too shallow to support real manual alpha iteration. This change makes the detail panel useful as a research notebook rather than a summary card.

### User-visible changes

- formal alpha cards now expand into structured research notes
- weak-evidence sources appear as ideas instead of misleading formal alphas
- detail cards show stronger source grounding and clearer upgrade paths

### Validation

- open a strong-evidence alpha and confirm the structured detail fields render
- open a historical alpha and confirm lazy backfill still works
- confirm weak-evidence articles only appear in Idea Inbox

### Data impact

- extends alpha detail storage schema
- requires historical detail backfill on first open
