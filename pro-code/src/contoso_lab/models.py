from typing import Literal

from pydantic import BaseModel, Field


Category = Literal[
    "late_delivery",
    "damaged_item",
    "wrong_item",
    "missing_item",
    "billing",
    "fraud",
    "other",
]


class IntakeResult(BaseModel):
    category: Category
    sentiment: Literal["calm", "frustrated", "angry"]
    urgency: int = Field(ge=1, le=5)
    orderId: str | None
    productMentioned: str | None
    summary: str
    language: str
    needsClarification: bool
    clarifyingQuestion: str | None


class PolicyFinding(BaseModel):
    eligible: bool
    remedy: Literal["refund", "replacement", "repair", "store_credit", "exchange", "none"]
    maxAmount: float
    clause: str
    requiresManagerApproval: bool
    reasoning: str


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


class SimilarCase(BaseModel):
    ticketId: str
    summary: str
    resolution: str
    refundAmount: float
    csat: int


class HistoryFinding(BaseModel):
    similarCases: list[SimilarCase]
    commonResolution: str
    averageRefund: float
    repeatCustomer: bool
    confidence: Literal["high", "medium", "low"]


class Recommendation(BaseModel):
    action: Literal["refund", "replace", "repair", "store_credit", "escalate", "decline"]
    refundAmount: float
    rationale: str
    requiresApproval: bool
    confidence: Literal["high", "medium", "low"]
    customerContextNote: str | None
