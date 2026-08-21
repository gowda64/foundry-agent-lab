from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field


_REPO_ROOT = Path(__file__).resolve().parents[3]
_PRO_CODE_ROOT = _REPO_ROOT / "pro-code"
_DEFAULT_DATA_DIR = _REPO_ROOT / "data"
_DEFAULT_PROMPTS_DIR = _PRO_CODE_ROOT / "prompts"


class Settings(BaseModel):
    """Runtime settings for the pro-code lab.

    Paths are resolved from the repository layout rather than the current working
    directory, so commands work from either the repository root or `pro-code/`.
    """

    foundry_project_endpoint: str | None = None
    small_model_deployment: str = "gpt-4o-mini"
    large_model_deployment: str = "gpt-4o"
    data_dir: Path = Field(default_factory=lambda: _DEFAULT_DATA_DIR)
    prompts_dir: Path = Field(default_factory=lambda: _DEFAULT_PROMPTS_DIR)


def _resolve_path(value: str | None, default: Path) -> Path:
    if not value:
        return default
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    # Resolve relative paths from pro-code/, because .env lives there and the
    # sample .env uses DATA_DIR=../data.
    return (_PRO_CODE_ROOT / path).resolve()


@lru_cache
def get_settings() -> Settings:
    load_dotenv(_PRO_CODE_ROOT / ".env")
    return Settings(
        foundry_project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        small_model_deployment=os.getenv("SMALL_MODEL_DEPLOYMENT", "gpt-4o-mini"),
        large_model_deployment=os.getenv("LARGE_MODEL_DEPLOYMENT", "gpt-4o"),
        data_dir=_resolve_path(os.getenv("DATA_DIR"), _DEFAULT_DATA_DIR),
        prompts_dir=_resolve_path(os.getenv("PROMPTS_DIR"), _DEFAULT_PROMPTS_DIR),
    )
