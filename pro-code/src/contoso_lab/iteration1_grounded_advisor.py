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
    """Run the single-agent Grounded Advisor through Foundry-hosted agents.

    Local files are loaded only to verify seed prompts/data exist for the lab. The
    actual policy and tone retrieval should come from Foundry IQ / agent knowledge.
    """
    settings = get_settings()
    _ = read_text(settings.prompts_dir / "complaint_advisor.md")
    _ = read_text(settings.data_dir / "returns-policy.md")
    _ = read_text(settings.data_dir / "tone-of-voice.md")

    active_client = client or default_client()
    intake = await active_client.run_intake(complaint_text)
    policy_finding = await active_client.run_policy(intake)
    if "POLICY_UNCLEAR" in policy_finding.reasoning:
        return f"STEP 1 — UNDERSTAND\n{intake.summary}\n\nSTEP 2 — POLICY VERDICT\n{policy_finding.reasoning}"
    draft = await active_client.write_response(intake, policy_finding)
    approval_line = "\n⚠️ MANAGER APPROVAL REQUIRED before sending.\n" if policy_finding.requiresManagerApproval else "\n"
    return (
        "STEP 1 — UNDERSTAND\n"
        f"Category: {intake.category}\n"
        f"Sentiment: {intake.sentiment}\n"
        f"Order ID: {intake.orderId or 'not provided'}\n\n"
        "STEP 2 — POLICY VERDICT\n"
        f"Eligible: {policy_finding.eligible}\n"
        f"Remedy: {policy_finding.remedy}\n"
        f"Maximum amount: ${policy_finding.maxAmount:.2f}\n"
        f"Clause: {policy_finding.clause}\n"
        f"Manager approval required: {policy_finding.requiresManagerApproval}\n"
        f"{approval_line}\n"
        "STEP 3 — DRAFT REPLY\n"
        f"{draft}"
    )
