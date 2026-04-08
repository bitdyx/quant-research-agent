# Quant Research Agent

`quant_research_agent` is a conservative daily quant research workflow that:

- collects 5-10 quant papers or blog posts from a whitelist,
- avoids re-researching content already stored in SQLite,
- generates 1-3 conservative WorldQuant-style alpha expressions per article,
- validates each alpha once in WorldQuant,
- stores runs, articles, alphas, and metrics in a local database,
- opens a local web dashboard by default, while keeping the legacy GUI viewer as a fallback.

## Commands

Run from `D:\python\worldquant\quant_research_agent`:

```powershell
D:\program\Anaconda\python.exe .\run_agent.py
D:\program\Anaconda\python.exe .\run_agent.py run-daily
D:\program\Anaconda\python.exe .\run_agent.py collect
D:\program\Anaconda\python.exe .\run_agent.py report --date 2026-04-06
D:\program\Anaconda\python.exe .\run_agent.py open-web
D:\program\Anaconda\python.exe .\run_agent.py open-gui
```

- `run_agent.py` with no arguments: open the local web dashboard
- `run_agent.py open-web`: explicitly open the local web dashboard
- `run_agent.py open-gui`: open the legacy Tk viewer
- `run_agent.py <command>`: run the CLI command

## Credentials

By default the validator reuses credentials already present in `alpha_miner_basics.py`.
You can override them with environment variables:

- `WQB_USERNAME`
- `WQB_PASSWORD`

## Storage

- SQLite database: `data/research_agent.sqlite3`
- Markdown exports: `data/reports/`

## GitHub workflow

This project is prepared to use GitHub as its collaboration hub.

- Local repository root: `D:\python\worldquant\quant_research_agent`
- Branch naming: `main` for stable history, `codex/...` for work branches
- Pull requests should use the template in `.github/pull_request_template.md`
- Seed backlog items live in `docs/github_backlog_seed.md`
- Remote/bootstrap steps live in `docs/github_bootstrap.md`

Important:

- runtime SQLite files and generated exports stay local and are ignored by git
- GitHub should track code, backlog, and PR review; the local dashboard should keep daily run data

## Notes

- First version focuses on long-term memory, not exact mid-run checkpoint resume.
- It avoids duplicate research by checking stored URL/title/content hashes before reprocessing articles.
- The web dashboard is now the main inspection surface for daily runs and alpha results.
- The dashboard also exposes a `Run Daily Research` button with live status polling.
