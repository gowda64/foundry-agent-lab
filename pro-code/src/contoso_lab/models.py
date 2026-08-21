from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


Category = Literal[
    "late_delivery",
    "damaged_item",
    "wrong_item",
    "missing_item",
    "billing",
    "fraud",
    "other",
]

Sentiment = Literal["calm", "frustrated", "angry"]
Confidence = Literal["high", "medium", "low"]
Remedy = Literal["refund", "replacement", "repair", "store_credit", "exchange", "none"]
Action = Literal["refund", "replace", "repair", "store_credit", "escalate", "decline"]


class IntakeResult(BaseModel):
    category: Category
    sentiment: Sentiment
    urgency: int = Field(ge=1, le=5)
    orderId: str | None
    productMentioned: str | None
    summary: str = Field(min_length=1, max_length=180)
    language: str = Field(min_length=2, max_length=5)
    needsClarification: bool
    clarifyingQuestion: str | None

    @model_validator(mode="after")
    def require_question_when_clarification_needed(self) -> "IntakeResult":
        if self.needsClarification and not self.clarifyingQuestion:
            raise ValueError("clarifyingQuestion is required when needsClarification is true")
        return self


class PolicyFinding(BaseModel):
    eligible: bool
    remedy: Remedy
    maxAmount: float = Field(ge=0)
    clause: str
    requiresManagerApproval: bool
    reasoning: str = Field(min_length=1, max_length=300)

    @model_validator(mode="after")
    def policy_unclear_uses_no_remedy(self) -> "PolicyFinding":
        if "POLICY_UNCLEAR" in self.reasoning and self.remedy != "none":
            raise ValueError("POLICY_UNCLEAR findings must use remedy='none'")
        return self


class OrderDetails(BaseModel):
    orderId: str | None
    customerId: str | None
    customer: str | None
    item: str | None
    amount: float | None
    orderDate: str | None
    deliveryDate: str | None
    status: str | None
    paymentMethod: str | None
    daysSinceDelivery: int | None
    found: bool

    @model_validator(mode="after")
    def unknown_orders_do_not_contain_fabricated_facts(self) -> "OrderDetails":
        if not self.found:
            fabricated_fields = [
                self.customerId,
                self.customer,
                self.item,
                self.amount,
                self.orderDate,
                self.deliveryDate,
                self.status,
                self.paymentMethod,
                self.daysSinceDelivery,
            ]
            if any(value is not None for value in fabricated_fields):
                raise ValueError("found=false orders must not include fabricated order facts")
        return self


class SimilarCase(BaseModel):
    ticketId: str
    summary: str
    resolution: str
    refundAmount: float = Field(ge=0)
    csat: int = Field(ge=1, le=5)


class HistoryFinding(BaseModel):
    similarCases: list[SimilarCase] = Field(default_factory=list, max_length=3)
    commonResolution: str
    averageRefund: float = Field(ge=0)
    repeatCustomer: bool
    confidence: Confidence


class Recommendation(BaseModel):
    action: Action
    refundAmount: float = Field(ge=0)
    rationale: str = Field(min_length=1, max_length=400)
    requiresApproval: bool
    confidence: Confidence
    customerContextNote: str | None

    @field_validator("refundAmount")
    @classmethod
    def round_refund_amount(cls, value: float) -> float:
        return round(value, 2)
