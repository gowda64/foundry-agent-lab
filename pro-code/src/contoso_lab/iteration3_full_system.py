from __future__ import annotations

import asyncio

from .config import get_settings
from .data_sources import find_similar_tickets, lookup_order
from .iteration2_first_workflow import extract_customer_id, run_intake, run_policy, run_response_writer
from .models import HistoryFinding, IntakeResult, OrderDetails, PolicyFinding, Recommendation


async def run_order_lookup(intake: IntakeResult) -> OrderDetails:
    """Use deterministic CSV lookup first; optionally wrap as an Agent Framework tool."""
    settings = get_settings()
    return lookup_order(settings.data_dir, intake.orderId)


async def run_history(intake: IntakeResult, complaint_text: str = "") -> HistoryFinding:
    """Local reference History Agent over past-tickets.csv."""
    settings = get_settings()
    return find_similar_tickets(settings.data_dir, intake.category, intake.summary, extract_customer_id(complaint_text))


async def run_resolution(
    intake: IntakeResult,
    order_details: OrderDetails,
    policy_finding: PolicyFinding,
    history: HistoryFinding,
) -> Recommendation:
    """Local reference Resolution Agent."""
    if not order_details.found:
        return Recommendation(
            action="escalate",
            refundAmount=0,
            rationale="Order details were not found, so no refund can be recommended without human review.",
            requiresApproval=True,
            confidence="low",
            customerContextNote="Order lookup returned found=false.",
        )

    if not policy_finding.eligible or "POLICY_UNCLEAR" in policy_finding.reasoning:
        return Recommendation(
            action="escalate" if "POLICY_UNCLEAR" in policy_finding.reasoning else "decline",
            refundAmount=0,
            rationale=policy_finding.reasoning,
            requiresApproval=policy_finding.requiresManagerApproval,
            confidence="low" if "POLICY_UNCLEAR" in policy_finding.reasoning else "medium",
            customerContextNote=None,
        )

    if policy_finding.remedy == "refund":
        action = "refund"
        refund_amount = min(order_details.amount or 0, policy_finding.maxAmount or order_details.amount or 0)
    elif policy_finding.remedy == "replacement":
        action = "replace"
        refund_amount = 0
    elif policy_finding.remedy == "store_credit":
        action = "store_credit"
        refund_amount = min(order_details.amount or 0, policy_finding.maxAmount or order_details.amount or 0)
    elif policy_finding.remedy == "repair":
        action = "repair"
        refund_amount = 0
    else:
        action = "decline"
        refund_amount = 0

    requires_approval = (
        refund_amount > 200
        or intake.category == "fraud"
        or policy_finding.requiresManagerApproval
        or history.repeatCustomer
    )
    context_note = None
    if history.similarCases:
        context_note = f"Similar cases usually resolved as: {history.commonResolution}; average refund ${history.averageRefund:.2f}."

    return Recommendation(
        action=action,  # type: ignore[arg-type]
        refundAmount=refund_amount,
        rationale=f"Policy finding is binding: {policy_finding.clause}",
        requiresApproval=requires_approval,
        confidence="high" if history.confidence in {"high", "medium"} else "medium",
        customerContextNote=context_note,
    )


async def request_human_approval(
    recommendation: Recommendation,
    order_details: OrderDetails,
    auto_decision: str | None = None,
) -> Recommendation:
    """Placeholder for the human approval node from the portal workflow.

    Replace with your actual approval channel. For the lab, CLI input is enough.
    Tests and demos can pass auto_decision to avoid blocking.
    """
    print(f"Approval required for refund ${recommendation.refundAmount:.2f} on order {order_details.orderId}")
    decision = (auto_decision or input("approve / reject / modify: ")).strip().lower()
    if decision == "reject":
        return recommendation.model_copy(update={"action": "decline", "refundAmount": 0, "requiresApproval": False})
    if decision == "approve":
        return recommendation.model_copy(update={"requiresApproval": False})
    if decision == "modify":
        amount = float(input("Modified refund amount: ").strip())
        capped = min(amount, order_details.amount or amount)
        return recommendation.model_copy(update={"refundAmount": capped, "requiresApproval": False})
    return recommendation


def approval_required(intake: IntakeResult, policy_finding: PolicyFinding, recommendation: Recommendation) -> bool:
    return (
        recommendation.refundAmount > 200
        or intake.category == "fraud"
        or policy_finding.requiresManagerApproval
        or recommendation.requiresApproval
    )


async def run_iteration3(complaint_text: str, auto_approve: bool = False) -> str:
    intake = await run_intake(complaint_text)

    order_details, policy_finding, history = await asyncio.gather(
        run_order_lookup(intake),
        _run_policy_with_order_context(intake),
        run_history(intake, complaint_text),
    )

    recommendation = await run_resolution(intake, order_details, policy_finding, history)

    if approval_required(intake, policy_finding, recommendation):
        auto_decision = "approve" if auto_approve else None
        recommendation = await request_human_approval(recommendation, order_details, auto_decision=auto_decision)

    return await run_response_writer(intake, policy_finding, order_details, recommendation)


async def _run_policy_with_order_context(intake: IntakeResult) -> PolicyFinding:
    order_details = await run_order_lookup(intake)
    return await run_policy(intake, order_details)
