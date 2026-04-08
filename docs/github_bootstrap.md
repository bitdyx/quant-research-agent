# GitHub Bootstrap Guide

This project is ready to use GitHub as its collaboration hub, but two environment steps still depend on the local machine owner:

1. restore the Codex GitHub plugin login
2. create or choose the remote GitHub repository

## 1. Restore GitHub access

Do this first so the GitHub plugin can read repositories, create issues, and open PRs again.

- Re-authenticate the GitHub plugin in Codex
- Confirm the token is no longer expired
- Verify that repository listing works before moving on

## 2. Create the remote repository

Recommended repository name:

- `quant_research_agent`

Suggested visibility:

- private first, then change later if wanted

## 3. Attach the local repository

Run from `D:\python\worldquant\quant_research_agent` after the remote repo exists:

```powershell
git remote add origin <your-github-repo-url>
git push -u origin main
```

## 4. Create the initial labels

Recommended labels:

- `research`
- `pipeline`
- `ui`
- `knowledge-base`
- `validation`
- `source-quality`
- `memory`
- `bug`

## 5. Seed the first backlog

Use `docs/github_backlog_seed.md` as the source of truth for the first GitHub issues. Create those issues before starting the next implementation wave.

## 6. Standard workflow after bootstrap

1. create or pick a GitHub issue
2. create a `codex/...` branch
3. implement locally
4. open a draft PR
5. validate locally
6. mark PR ready and merge

## Notes

- SQLite runtime data should stay local and should not be committed
- generated reports under `data/reports/` should stay ignored unless explicitly exported elsewhere
- use GitHub for roadmap, issue tracking, and PR review; use the local dashboard for daily run data
