from __future__ import annotations

import re

from .config import get_settings
from .data_sources import lookup_order, read_text
from .models import IntakeResult, OrderDetails, PolicyFinding, Recommendation

_ORDER_ID = re.compile(r"\bCR-\d{5}\b")
_CUSTOMER_ID = re.compile(r"customerId:\s*(?P<customer_id>\S+)", re.IGNORECASE)
_AMOUNT = re.compile(r"(?:\$|\b)(?P<amount>\d+(?:\.\d{1,2})?)\s*(?:dollars|usd)?", re.IGNORECASE)


def extract_customer_id(text: str) -> str | None:
    match = _CUSTOMER_ID.search(text)
    return match.group("customer_id") if match else None


def extract_order_id(text: str) -> str | None:
    match = _ORDER_ID.search(text)
    return match.group(0) if match else None


async def run_intake(complaint_text: str) -> IntakeResult:
    """Local reference Intake Agent.

    Replace this function with a Foundry-hosted Agent Framework call when you are
    ready to use live agents. The deterministic implementation keeps the skeleton
    runnable and validates the JSON contract.
    """
    text = complaint_text.strip()
    lower = text.lower()
    order_id = extract_order_id(text)

    if any(term in lower for term in ["fraud", "stealing", "card used", "never placed"]):
        category = "fraud"
        urgency = 5
    elif any(term in lower for term in ["wrong item", "sent me", "instead of"]):
        category = "wrong_item"
        urgency = 3
    elif any(term in lower for term in ["missing", "missing from", "not in the box"]):
        category = "missing_item"
        urgency = 3
    elif any(term in lower for term in ["late", "delayed", "didn't turn up", "hasn't shown up"]):
        category = "late_delivery"
        urgency = 3
    elif any(term in lower for term in ["charged", "billing", "refund not received"]):
        category = "billing"
        urgency = 3
    elif any(term in lower for term in ["damaged", "smashed", "cracked", "broken", "leaking", "dented", "flaking", "cassée"]):
        category = "damaged_item"
        urgency = 3
    else:
        category = "other"
        urgency = 2

    sentiment = "angry" if any(term in lower for term in ["joke", "stealing", "refund me", "immediately"]) else "frustrated"
    if any(term in lower for term in ["please", "merci", "hi,"]):
        sentiment = "calm" if sentiment != "angry" else sentiment

    product = _extract_product(text)
    language = "fr" if any(term in lower for term in ["bonjour", "commande", "remboursement", "s'il vous plaît"]) else "en"
    needs_clarification = order_id is None
    summary = _summarise(text, category, product)

    return IntakeResult(
        category=category,  # type: ignore[arg-type]
        sentiment=sentiment,  # type: ignore[arg-type]
        urgency=urgency,
        orderId=order_id,
        productMentioned=product,
        summary=summary,
        language=language,
        needsClarification=needs_clarification,
        clarifyingQuestion="What is your order ID?" if needs_clarification else None,
    )


async def run_policy(intake: IntakeResult, order_details: OrderDetails | None = None) -> PolicyFinding:
    """Local reference Policy Agent.

    The portal Iteration 2 Policy Agent is grounded in returns-policy.md. This
    deterministic version encodes the same key lab rules so local tests and CLI
    runs behave predictably before a live model is connected.
    """
    settings = get_settings()
    _ = read_text(settings.data_dir / "returns-policy.md")

    amount = order_details.amount if order_details and order_details.amount is not None else _extract_amount(intake.summary)
    days = order_details.daysSinceDelivery if order_details else None

    if "cryptocurrency" in intake.summary.lower() or "crypto" in intake.summary.lower():
        return PolicyFinding(
            eligible=False,
            remedy="none",
            maxAmount=0,
            clause="10.1 Cases the agent cannot resolve under this policy must be escalated to a human manager with a written rationale.",
            requiresManagerApproval=True,
            reasoning="POLICY_UNCLEAR: the policy does not address cryptocurrency refunds.",
        )

    if intake.category == "fraud":
        return PolicyFinding(
            eligible=True,
            remedy="refund",
            maxAmount=amount or 0,
            clause="5.2 Any case categorised as fraud or suspected fraud requires manager approval regardless of value.",
            requiresManagerApproval=True,
            reasoning="Suspected fraud requires manager approval regardless of refund value.",
        )

    if intake.category == "damaged_item":
        if days is not None and days > 14:
            return PolicyFinding(
                eligible=True,
                remedy="repair",
                maxAmount=0,
                clause="3.3 Items reported damaged after 14 days fall under section 4.",
                requiresManagerApproval=False,
                reasoning="Damage reported after 14 days should be handled as a faulty item rather than damaged on arrival.",
            )
        return PolicyFinding(
            eligible=True,
            remedy="refund",
            maxAmount=amount or 0,
            clause="3.1 Items reported damaged within 14 days of delivery are eligible for a full refund or free replacement, at the customer's choice.",
            requiresManagerApproval=(amount or 0) > 200,
            reasoning="Damaged-on-arrival items reported within 14 days are eligible for refund or replacement.",
        )

    if intake.category == "wrong_item":
        return PolicyFinding(
            eligible=True,
            remedy="replacement",
            maxAmount=amount or 0,
            clause="6.1 Wrong item shipped: full refund or correct item dispatched free, customer's choice, within 30 days.",
            requiresManagerApproval=(amount or 0) > 200,
            reasoning="Wrong item shipped allows a refund or correct item dispatch within 30 days.",
        )

    if intake.category == "missing_item":
        return PolicyFinding(
            eligible=True,
            remedy="replacement",
            maxAmount=amount or 0,
            clause="6.2 Missing item from a multi-item order: dispatch the missing item, or refund that line, within 30 days.",
            requiresManagerApproval=(amount or 0) > 200,
            reasoning="Missing item cases allow dispatching the missing item or refunding that line.",
        )

    if intake.category == "late_delivery":
        return PolicyFinding(
            eligible=True,
            remedy="refund",
            maxAmount=0,
            clause="7.1 Delivery more than 5 days beyond the promised date entitles the customer to a refund of the delivery charge.",
            requiresManagerApproval=False,
            reasoning="Late delivery over five days allows refunding the delivery charge only.",
        )

    return PolicyFinding(
        eligible=False,
        remedy="none",
        maxAmount=0,
        clause="10.1 Cases the agent cannot resolve under this policy must be escalated to a human manager with a written rationale.",
        requiresManagerApproval=True,
        reasoning=f"POLICY_UNCLEAR: category '{intake.category}' needs human review for this lab scenario.",
    )


async def run_response_writer(
    intake: IntakeResult,
    policy_finding: PolicyFinding,
    order_details: OrderDetails | None = None,
    recommendation: Recommendation | None = None,
) -> str:
    """Local reference Response Writer Agent."""
    settings = get_settings()
    _ = read_text(settings.data_dir / "tone-of-voice.md")

    first_name = (order_details.customer.split()[0] if order_details and order_details.customer else "there")
    amount = recommendation.refundAmount if recommendation else policy_finding.maxAmount
    payment = _format_payment(order_details.paymentMethod) if order_details and order_details.paymentMethod else "your original payment method"

    if intake.needsClarification:
        return (
            f"Hi {first_name},\n\n"
            "I'm sorry this has been frustrating. I need one detail before I can look into it properly: "
            f"{intake.clarifyingQuestion}\n\n"
            "Once you send that over, I can check the order and confirm the next step."
        )

    if recommendation and recommendation.action == "decline" or not policy_finding.eligible:
        return (
            f"Hi {first_name},\n\n"
            "I'm sorry this was not the answer you were hoping for. I'm not able to refund this one based on the details available, "
            "but I can escalate it for a manager to review and confirm whether another option is available.\n\n"
            "The next step is to review the case within 2 working days and come back with a clear answer. "
            "If you have photos or delivery updates, please include them so we can assess it fully."
        )

    action = recommendation.action if recommendation else policy_finding.remedy
    if action in {"refund", "store_credit"} and amount > 0:
        outcome = f"I've arranged a refund of ${amount:.2f} to {payment}. It'll land within 5 working days."
    elif action in {"replace", "replacement"}:
        outcome = "I'll arrange a free replacement so the correct item is sent to you."
    elif action == "repair":
        outcome = "I'll arrange a repair or replacement assessment for the item."
    else:
        outcome = "I'll escalate this so a manager can review the best available remedy."

    return (
        f"Hi {first_name},\n\n"
        f"I'm sorry your order has not arrived as expected. {outcome}\n\n"
        "The next step is that we will confirm the action within 1 working day and send any return or replacement details you need. "
        "You do not need to repeat the issue or contact another team.\n\n"
        "If anything in the order details is incorrect, reply with the updated information and I will help from there."
    )


async def run_iteration2(complaint_text: str) -> str:
    intake = await run_intake(complaint_text)
    policy_finding = await run_policy(intake)
    return await run_response_writer(intake, policy_finding)


def _extract_product(text: str) -> str | None:
    known_products = [
        "BrewMaster coffee machine",
        "Espresso Machine Deluxe",
        "AirGlide vacuum",
        "milk frother",
        "induction hob",
        "StandMixer 5L",
        "herb garden kit",
        "Juicer Pro",
        "cookware bundle",
        "kettle",
    ]
    lower = text.lower()
    for product in known_products:
        if product.lower() in lower:
            return product
    return None


def _summarise(text: str, category: str, product: str | None) -> str:
    clean = re.sub(r"customerId:\s*\S+", "", text, flags=re.IGNORECASE).strip()
    clean = re.sub(r"\s+", " ", clean)
    if product:
        return f"Customer reports {category.replace('_', ' ')} for {product}."
    return clean[:160]


def _extract_amount(text: str) -> float:
    amounts = [float(match.group("amount")) for match in _AMOUNT.finditer(text)]
    return max(amounts) if amounts else 0


def _format_payment(payment_method: str) -> str:
    return payment_method.replace("_", " ").replace("ending", "ending")
