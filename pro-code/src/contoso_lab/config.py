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

    The files in `data/` are seed assets for uploading to Foundry IQ / Foundry
    Agent knowledge. The pro-code runtime should retrieve business facts through
    Foundry IQ and Foundry tools, not by reading local CSV files as a database.
    """

    foundry_project_endpoint: str | None = None
    small_model_deployment: str = "gpt-4o-mini"
    large_model_deployment: str = "gpt-4o"
    foundry_iq_knowledge_base_id: str | None = None
    foundry_iq_knowledge_base_name: str = "contoso-retail-lab"
    order_lookup_tool_name: str = "contoso-order-lookup"
    history_search_tool_name: str = "contoso-ticket-history-search"
    data_dir: Path = Field(default_factory=lambda: _DEFAULT_DATA_DIR)
    prompts_dir: Path = Field(default_factory=lambda: _DEFAULT_PROMPTS_DIR)

    @property
    def foundry_configured(self) -> bool:
        return bool(self.foundry_project_endpoint)


def _resolve_path(value: str | None, default: Path) -> Path:
    if not value:
        return default
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (_PRO_CODE_ROOT / path).resolve()


@lru_cache
def get_settings() -> Settings:
    load_dotenv(_PRO_CODE_ROOT / ".env")
    return Settings(
        foundry_project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        small_model_deployment=os.getenv("SMALL_MODEL_DEPLOYMENT", "gpt-4o-mini"),
        large_model_deployment=os.getenv("LARGE_MODEL_DEPLOYMENT", "gpt-4o"),
        foundry_iq_knowledge_base_id=os.getenv("FOUNDRY_IQ_KNOWLEDGE_BASE_ID"),
        foundry_iq_knowledge_base_name=os.getenv("FOUNDRY_IQ_KNOWLEDGE_BASE_NAME", "contoso-retail-lab"),
        order_lookup_tool_name=os.getenv("ORDER_LOOKUP_TOOL_NAME", "contoso-order-lookup"),
        history_search_tool_name=os.getenv("HISTORY_SEARCH_TOOL_NAME", "contoso-ticket-history-search"),
        data_dir=_resolve_path(os.getenv("DATA_DIR"), _DEFAULT_DATA_DIR),
        prompts_dir=_resolve_path(os.getenv("PROMPTS_DIR"), _DEFAULT_PROMPTS_DIR),
    )
