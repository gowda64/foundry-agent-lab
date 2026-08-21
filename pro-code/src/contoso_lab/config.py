from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import BaseModel


class Settings(BaseModel):
    foundry_project_endpoint: str | None = None
    small_model_deployment: str = "gpt-4o-mini"
    large_model_deployment: str = "gpt-4o"
    data_dir: Path = Path("../data")


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        foundry_project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        small_model_deployment=os.getenv("SMALL_MODEL_DEPLOYMENT", "gpt-4o-mini"),
        large_model_deployment=os.getenv("LARGE_MODEL_DEPLOYMENT", "gpt-4o"),
        data_dir=Path(os.getenv("DATA_DIR", "../data")),
    )
