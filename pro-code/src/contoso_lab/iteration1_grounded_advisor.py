from __future__ import annotations

import re

from .config import get_settings
from .data_sources import read_text
from .foundry_client import ContosoFoundryClient, FoundryAgentClient

_CUSTOMER_ID = re.compile(r"customerId:\s*(?P<customer_id>\S+)", re.IGNORECASE)
_ORDER_ID = re.compile(r"\bCR-\d{5}\b")


def extract_customer_id(text: str) -> str | None:
    match = _CUSTOMER_ID.search(text)
    return match.group("customer_id") if match else None


def extract_order_id(text: str) -> str | None:
    match = _ORDER_ID.search(text)
    return match.group(0) if match else None


def default_client() -> ContosoFoundryClient:
    return FoundryAgentClient(get_settings())


async def run_iteration1(complaint_text: str, client: ContosoFoundryClient | None = None) -> str:
    """Run Iteration 1 as one grounded Complaint Advisor agent.

    Local files are loaded only to verify seed prompts/data exist for the lab. The
    actual policy and tone retrieval should come from Foundry IQ / agent knowledge.
    """
    settings = get_settings()
    _ = read_text(settings.prompts_dir / "complaint_advisor.md")
    _ = read_text(settings.data_dir / "returns-policy.md")
    _ = read_text(settings.data_dir / "tone-of-voice.md")

    active_client = client or default_client()
    return await active_client.run_complaint_advisor(complaint_text)
