from contoso_lab.models import IntakeResult, PolicyFinding, Recommendation
from contoso_lab.iteration3_full_system import approval_required


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
