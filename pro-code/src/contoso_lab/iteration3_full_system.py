from __future__ import annotations

import asyncio

from .config import get_settings
from .data_sources import lookup_order
from .iteration2_first_workflow import run_intake, run_policy, run_response_writer
from .models import HistoryFinding, IntakeResult, OrderDetails, PolicyFinding, Recommendation


async def run_order_lookup(intake: IntakeResult) -> OrderDetails:
    """Use deterministic CSV lookup first; optionally wrap as an Agent Framework tool."""
    settings = get_settings()
    return lookup_order(settings.data_dir, intake.orderId)


async def run_history(intake: IntakeResult) -> HistoryFinding:
    """TODO: call the History Agent over past-tickets.csv and parse JSON."""
    raise NotImplementedError


async def run_resolution(
    intake: IntakeResult,
    order_details: OrderDetails,
    policy_finding: PolicyFinding,
    history: HistoryFinding,
) -> Recommendation:
    """TODO: call the Resolution Agent and parse JSON into Recommendation."""
    raise NotImplementedError


async def request_human_approval(recommendation: Recommendation, order_details: OrderDetails) -> Recommendation:
    """Placeholder for the human approval node from the portal workflow.

    Replace with your actual approval channel. For the lab, CLI input is enough.
    """
    print(f"Approval required for refund ${recommendation.refundAmount:.2f} on order {order_details.orderId}")
    decision = input("approve / reject / modify: ").strip().lower()
    if decision == "reject":
        return recommendation.model_copy(update={"action": "decline", "refundAmount": 0, "requiresApproval": False})
    if decision == "approve":
        return recommendation.model_copy(update={"requiresApproval": False})
    if decision == "modify":
        amount = float(input("Modified refund amount: ").strip())
        return recommendation.model_copy(update={"refundAmount": amount, "requiresApproval": False})
    return recommendation


def approval_required(intake: IntakeResult, policy_finding: PolicyFinding, recommendation: Recommendation) -> bool:
    return (
        recommendation.refundAmount > 200
        or intake.category == "fraud"
        or policy_finding.requiresManagerApproval
        or recommendation.requiresApproval
    )


async def run_iteration3(complaint_text: str) -> str:
    intake = await run_intake(complaint_text)

    order_details, policy_finding, history = await asyncio.gather(
        run_order_lookup(intake),
        run_policy(intake),
        run_history(intake),
    )

    recommendation = await run_resolution(intake, order_details, policy_finding, history)

    if approval_required(intake, policy_finding, recommendation):
        recommendation = await request_human_approval(recommendation, order_details)

    # TODO: update Response Writer to accept recommendation and order details for Iteration 3.
    _ = recommendation
    return await run_response_writer(intake, policy_finding)
