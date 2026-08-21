from __future__ import annotations

from .config import get_settings
from .data_sources import read_text
from .iteration2_first_workflow import run_intake, run_policy, run_response_writer


async def run_iteration1(complaint_text: str) -> str:
    """Run the single-agent Grounded Advisor local reference flow.

    This keeps the lab executable before learners wire in Microsoft Agent
    Framework. The policy and tone guide are loaded to verify required files are
    present; the deterministic advisor logic reuses the Iteration 2 components so
    the same contracts are exercised locally.
    """
    settings = get_settings()
    prompt = read_text(settings.prompts_dir / "complaint_advisor.md")
    returns_policy = read_text(settings.data_dir / "returns-policy.md")
    tone_guide = read_text(settings.data_dir / "tone-of-voice.md")

    _ = (prompt, returns_policy, tone_guide)
    intake = await run_intake(complaint_text)
    policy_finding = await run_policy(intake)
    if "POLICY_UNCLEAR" in policy_finding.reasoning:
        return f"STEP 1 — UNDERSTAND\n{intake.summary}\n\nSTEP 2 — POLICY VERDICT\n{policy_finding.reasoning}"

    draft = await run_response_writer(intake, policy_finding)
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
