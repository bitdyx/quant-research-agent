from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PACKAGE_ROOT.parent
PROJECT_ROOT = SRC_ROOT.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = DATA_DIR / "reports"
KNOWLEDGE_EXPORTS_DIR = DATA_DIR / "knowledge_exports"
DOCS_DIR = PROJECT_ROOT / "docs"
DB_PATH = DATA_DIR / "research_agent.sqlite3"
SOURCES_PATH = CONFIG_DIR / "sources.json"
OPERATOR_SEED_PATH = CONFIG_DIR / "operator_seed.json"
ALPHA_MINER_PATH = WORKSPACE_ROOT / "alpha_miner_basics.py"


def ensure_project_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
