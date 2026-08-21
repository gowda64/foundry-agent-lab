from datetime import date

from contoso_lab.config import get_settings
from contoso_lab.data_sources import load_sample_complaints, lookup_order
from contoso_lab.iteration2_first_workflow import run_intake
from contoso_lab.iteration3_full_system import approval_required
from contoso_lab.models import IntakeResult, PolicyFinding, Recommendation


def test_data_dir_resolves_to_preloaded_data() -> None:
    settings = get_settings()
    assert (settings.data_dir / "orders.csv").exists()
    assert (settings.data_dir / "sample-complaints.md").exists()


def test_sample_complaints_parser_loads_cases() -> None:
    cases = load_sample_complaints(get_settings().data_dir)
    assert "1" in cases
    assert "CR-10432" in cases["1"]
    assert "customerId: CUST-8801" in cases["1"]


def test_known_order_lookup_returns_real_data() -> None:
    result = lookup_order(get_settings().data_dir, "CR-10432", today=date(2026, 8, 21))
    assert result.found is True
    assert result.customer == "Rita Sandoval"
    assert result.amount == 189.00
    assert result.daysSinceDelivery == 19


def test_unknown_order_does_not_fabricate() -> None:
    result = lookup_order(get_settings().data_dir, "CR-99999", today=date(2026, 8, 21))
    assert result.found is False
    assert result.customer is None
    assert result.amount is None


def test_high_value_refund_requires_approval() -> None:
    intake = IntakeResult(
        category="damaged_item",
        sentiment="frustrated",
        urgency=3,
        orderId="CR-10455",
        productMentioned="Espresso Machine Deluxe",
        summary="High-value espresso machine arrived damaged.",
        language="en",
        needsClarification=False,
        clarifyingQuestion=None,
    )
    policy = PolicyFinding(
        eligible=True,
        remedy="refund",
        maxAmount=450,
        clause="3.1 Items reported damaged within 14 days...",
        requiresManagerApproval=True,
        reasoning="Damaged on arrival and refund exceeds threshold.",
    )
    recommendation = Recommendation(
        action="refund",
        refundAmount=450,
        rationale="Eligible under policy but exceeds approval threshold.",
        requiresApproval=True,
        confidence="high",
        customerContextNote=None,
    )
    assert approval_required(intake, policy, recommendation) is True


def test_fraud_requires_approval_even_under_threshold() -> None:
    intake = IntakeResult(
        category="fraud",
        sentiment="angry",
        urgency=5,
        orderId="CR-10450",
        productMentioned="Milk Frother",
        summary="Customer reports suspected fraud and non-delivery.",
        language="en",
        needsClarification=False,
        clarifyingQuestion=None,
    )
    policy = PolicyFinding(
        eligible=True,
        remedy="refund",
        maxAmount=26,
        clause="5.2 Any case categorised as fraud or suspected fraud requires manager approval regardless of value.",
        requiresManagerApproval=True,
        reasoning="Fraud category requires approval.",
    )
    recommendation = Recommendation(
        action="refund",
        refundAmount=26,
        rationale="Low value but suspected fraud.",
        requiresApproval=True,
        confidence="medium",
        customerContextNote=None,
    )
    assert approval_required(intake, policy, recommendation) is True


def test_no_order_complaint_contract() -> None:
    intake = IntakeResult(
        category="late_delivery",
        sentiment="angry",
        urgency=3,
        orderId=None,
        productMentioned=None,
        summary="Customer says a recent delivery has not arrived properly.",
        language="en",
        needsClarification=True,
        clarifyingQuestion="What is your order ID?",
    )
    assert intake.needsClarification is True
    assert intake.orderId is None
    assert intake.clarifyingQuestion


async def test_intake_ignores_prompt_injection() -> None:
    cases = load_sample_complaints(get_settings().data_dir)
    intake = await run_intake(cases["8"])
    assert intake.orderId == "CR-10456"
    assert intake.category != "fraud"
    assert intake.needsClarification is False
