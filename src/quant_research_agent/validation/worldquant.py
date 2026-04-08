import importlib.util
import os

import requests
from requests.auth import HTTPBasicAuth

from quant_research_agent.models import ArticleSummary, ValidationResult, ValidationSettings
from quant_research_agent.paths import ALPHA_MINER_PATH


_ALPHA_MINER_MODULE = None


def load_alpha_miner_module():
    global _ALPHA_MINER_MODULE
    if _ALPHA_MINER_MODULE is not None:
        return _ALPHA_MINER_MODULE

    spec = importlib.util.spec_from_file_location("alpha_miner_basics_runtime", ALPHA_MINER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load alpha_miner_basics.py from {ALPHA_MINER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _ALPHA_MINER_MODULE = module
    return module


def choose_validation_settings(summary: ArticleSummary) -> ValidationSettings:
    settings = ValidationSettings()
    if summary.suggested_universe in {"TOP500", "TOP1000"}:
        settings.universe = summary.suggested_universe
        settings.settings_reason = f"Article suggested a large-cap bias, so universe was tightened to {settings.universe}."
    if summary.is_daily_signal:
        settings.decay = 0
        extra = "Article looked daily-frequency, so decay was set to 0."
        settings.settings_reason = (
            f"{settings.settings_reason} {extra}" if settings.settings_reason != "default baseline" else extra
        )
    return settings


def _resolve_credentials(module) -> tuple[str, str]:
    username = os.getenv("WQB_USERNAME") or getattr(module, "USERNAME", "")
    password = os.getenv("WQB_PASSWORD") or getattr(module, "PASSWORD", "")
    if not username or not password:
        raise RuntimeError("WorldQuant credentials are missing. Set WQB_USERNAME/WQB_PASSWORD or update alpha_miner_basics.py.")
    return username, password


def _create_authenticated_session(username: str, password: str) -> requests.Session:
    session = requests.Session()
    session.auth = HTTPBasicAuth(username, password)
    response = session.post("https://api.worldquantbrain.com/authentication")
    response.raise_for_status()
    return session


def validate_expression(alpha_candidate_id: int, expression: str, summary: ArticleSummary) -> ValidationResult:
    module = load_alpha_miner_module()
    username, password = _resolve_credentials(module)
    session = _create_authenticated_session(username, password)
    settings = choose_validation_settings(summary)
    runtime_settings = module.RuntimeSettings(
        region=settings.region,
        delay=str(settings.delay),
        universe=settings.universe,
        neutralization=settings.neutralization,
        decay=settings.decay,
        truncation=settings.truncation,
        vector_transform="vec_avg",
    )
    simulation_settings = module.build_simulation_settings(runtime_settings)
    metrics = module.simulate_expression(
        sess=session,
        expression=expression,
        settings=simulation_settings,
        parameters=None,
        progress_callback=None,
        log_event_kind="log",
    )
    return ValidationResult(
        alpha_candidate_id=alpha_candidate_id,
        expression=expression,
        settings=settings,
        sharpe=metrics.sharpe,
        fitness=metrics.fitness,
        returns=metrics.returns,
        turnover=metrics.turnover,
        alpha_id=metrics.alpha_id,
        error=metrics.error,
    )
