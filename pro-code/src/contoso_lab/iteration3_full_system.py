from __future__ import annotations

import asyncio

from .foundry_client import ContosoFoundryClient
from .iteration1_grounded_advisor import default_client, extract_customer_id
from .iteration2_first_workflow import run_intake, run_policy, run_response_writer
from .models import ApprovalResult, HistoryFinding, IntakeResult, OrderDetails, PolicyFinding, Recommendation


async def run_order_lookup(intake: IntakeResult, client: ContosoFoundryClient | None = None) -> OrderDetails:
    """Call the Foundry order lookup tool.

    This intentionally does not read data/orders.csv. For the lab, upload the seed
    file to Foundry IQ or expose it through a Foundry tool that behaves like the
    real order system.
    """
    return await (client or default_client()).lookup_order(intake.orderId)


async def run_history(
    intake: IntakeResult,
    complaint_text: str = "",
    client: ContosoFoundryClient | None = None,
) -> HistoryFinding:
    """Call the Foundry history search tool over uploaded support-ticket data."""
    return await (client or default_client()).search_history(intake, extract_customer_id(complaint_text))


async def run_resolution(
    intake: IntakeResult,
    order_details: OrderDetails,
    policy_finding: PolicyFinding,
    history: HistoryFinding,
    client: ContosoFoundryClient | None = None,
) -> Recommendation:
    """Run the Resolution Agent in Foundry."""
    return await (client or default_client()).resolve(intake, order_details, policy_finding, history)


async def request_human_approval(
    recommendation: Recommendation,
    order_details: OrderDetails,
    client: ContosoFoundryClient | None = None,
    auto_decision: str | None = None,
) -> Recommendation:
    """Call the human approval Foundry tool or use auto_decision for demos/tests."""
    if auto_decision:
        approval = ApprovalResult(decision="approve" if auto_decision == "approve" else "reject")
    else:
        approval = await (client or default_client()).request_approval(recommendation, order_details)

    if approval.decision == "reject":
        return recommendation.model_copy(update={"action": "decline", "refundAmount": 0, "requiresApproval": False})
    if approval.decision == "approve":
        return recommendation.model_copy(update={"requiresApproval": False})
    if approval.decision == "modify":
        amount = approval.refundAmount if approval.refundAmount is not None else recommendation.refundAmount
        return recommendation.model_copy(update={"refundAmount": amount, "requiresApproval": False})
    return recommendation


def approval_required(intake: IntakeResult, policy_finding: PolicyFinding, recommendation: Recommendation) -> bool:
    return (
        recommendation.refundAmount > 200
        or intake.category == "fraud"
        or policy_finding.requiresManagerApproval
        or recommendation.requiresApproval
    )


async def run_iteration3(
    complaint_text: str,
    auto_approve: bool = False,
    client: ContosoFoundryClient | None = None,
) -> str:
    active_client = client or default_client()
    intake = await run_intake(complaint_text, active_client)

    order_details, policy_finding, history = await asyncio.gather(
        run_order_lookup(intake, active_client),
        run_policy(intake, active_client),
        run_history(intake, complaint_text, active_client),
    )

    recommendation = await run_resolution(intake, order_details, policy_finding, history, active_client)

    if approval_required(intake, policy_finding, recommendation):
        recommendation = await request_human_approval(
            recommendation,
            order_details,
            client=active_client,
            auto_decision="approve" if auto_approve else None,
        )

    return await run_response_writer(intake, policy_finding, order_details, recommendation, active_client)
