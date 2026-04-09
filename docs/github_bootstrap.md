# GitHub Bootstrap Guide

This project now has the basic GitHub plumbing in place.

## Current state

- local repo path: `D:\python\worldquant\quant_research_agent`
- remote repo: `https://github.com/bitdyx/quant-research-agent`
- default branch: `main`
- first feature branch: `codex/alpha-research-note-style`

## Operational notes

- The Codex GitHub connector is authenticated again and can read the repo when the transport layer is healthy.
- Local `git push` from this machine still hits intermittent TLS failures.
- Because of that, remote updates may temporarily use the GitHub connector as a fallback path instead of raw `git push`.
- Runtime data must remain local and ignored:
  - SQLite databases
  - exported reports
  - temporary test databases
  - local logs

## Initial labels

Recommended labels:

- `research`
- `pipeline`
- `ui`
- `knowledge-base`
- `validation`
- `source-quality`
- `memory`
- `bug`

## Backlog source of truth

Use these repository documents as the seed backlog until GitHub issue creation is stable again:

- `docs/github_backlog_seed.md`
- `docs/work_items/alpha-research-note-style.md`

Once direct GitHub issue creation is available, migrate those work items into GitHub and keep GitHub as the only active backlog.

## Standard workflow

1. create or select a backlog item
2. create or reuse a `codex/...` branch
3. implement locally
4. open a draft PR
5. validate locally
6. merge to `main`

## Notes

- SQLite runtime data should stay local and should not be committed
- generated reports under `data/reports/` should stay ignored unless explicitly exported elsewhere
- use GitHub for roadmap, issue tracking, and PR review; use the local dashboard for daily run data
