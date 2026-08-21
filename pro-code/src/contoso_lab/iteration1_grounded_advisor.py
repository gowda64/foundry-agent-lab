from pathlib import Path

from .config import get_settings
from .data_sources import read_text


def _prompt_path(file_name: str) -> Path:
    return Path(__file__).resolve().parents[2] / "prompts" / file_name


async def run_iteration1(complaint_text: str) -> str:
    """Run the single-agent Grounded Advisor.

    TODO:
    - Create a Microsoft Agent Framework agent backed by the Foundry large model.
    - Attach or inject returns-policy.md and tone-of-voice.md as grounding material.
    - Use prompts/complaint_advisor.md as the system instructions.
    - Return the raw advisor response.
    """
    settings = get_settings()
    prompt = read_text(_prompt_path("complaint_advisor.md"))
    returns_policy = read_text(settings.data_dir / "returns-policy.md")
    tone_guide = read_text(settings.data_dir / "tone-of-voice.md")

    _ = (prompt, returns_policy, tone_guide, complaint_text)
    raise NotImplementedError(
        "Wire Microsoft Agent Framework Foundry agent here using prompt, returns_policy, tone_guide, and complaint_text."
    )
