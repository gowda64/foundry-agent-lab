from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from pathlib import Path

from .models import HistoryFinding, OrderDetails, SimilarCase

_COMPLAINT_HEADING = re.compile(r"^###\s+(?P<number>\d+)\s+—\s+(?P<title>.+)$")
_CUSTOMER_ID = re.compile(r"^customerId:\s*(?P<customer_id>\S+)\s*$")
_QUOTED_BLOCK = re.compile(r'"(?P<text>.*)"', re.DOTALL)


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing required lab data file: {path}")
    return path.read_text(encoding="utf-8")


def load_sample_complaints(data_dir: Path) -> dict[str, str]:
    """Parse data/sample-complaints.md into complaint text keyed by case number.

    The returned text includes the customerId header when present, followed by the
    quoted customer complaint. That keeps CLI runs faithful to the lab data while
    still giving the Intake Agent one plain text payload.
    """
    path = data_dir / "sample-complaints.md"
    content = read_text(path)
    cases: dict[str, str] = {}
    current_number: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_number, current_lines
        if current_number is None:
            return
        block = "\n".join(current_lines).strip()
        customer_id = None
        body_lines: list[str] = []
        for line in block.splitlines():
            match = _CUSTOMER_ID.match(line.strip())
            if match:
                customer_id = match.group("customer_id")
            else:
                body_lines.append(line)
        body = "\n".join(body_lines).strip()
        quoted = _QUOTED_BLOCK.search(body)
        complaint = quoted.group("text").strip() if quoted else body
        prefix = f"customerId: {customer_id}\n" if customer_id else ""
        cases[current_number] = f"{prefix}{complaint}".strip()

    for line in content.splitlines():
        heading = _COMPLAINT_HEADING.match(line)
        if heading:
            flush()
            current_number = heading.group("number")
            current_lines = []
        else:
            current_lines.append(line)
    flush()
    return cases


def lookup_order(data_dir: Path, order_id: str | None, today: date | None = None) -> OrderDetails:
    """Deterministic order lookup used by Iteration 3.

    Keep this non-generative: unknown orders must return found=False.
    """
    if not order_id:
        return _not_found(order_id)

    orders_path = data_dir / "orders.csv"
    if not orders_path.exists():
        raise FileNotFoundError(f"Missing required lab data file: {orders_path}")

    today = today or date.today()
    with orders_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["order_id"] == order_id:
                delivery_date = row["delivery_date"] or None
                days_since_delivery = None
                if delivery_date:
                    delivered = date.fromisoformat(delivery_date)
                    days_since_delivery = (today - delivered).days
                return OrderDetails(
                    orderId=row["order_id"],
                    customerId=row["customer_id"],
                    customer=row["customer"],
                    item=row["item"],
                    amount=float(row["amount"]),
                    orderDate=row["order_date"],
                    deliveryDate=delivery_date,
                    status=row["status"],
                    paymentMethod=row["payment_method"],
                    daysSinceDelivery=days_since_delivery,
                    found=True,
                )

    return _not_found(order_id)


def find_similar_tickets(data_dir: Path, category: str, summary: str, customer_id: str | None = None) -> HistoryFinding:
    """Deterministic local substitute for the History Agent.

    It keeps the lab runnable before learners replace this with a Foundry-hosted
    History Agent. Matching intentionally stays simple and transparent.
    """
    tickets_path = data_dir / "past-tickets.csv"
    if not tickets_path.exists():
        raise FileNotFoundError(f"Missing required lab data file: {tickets_path}")

    query_terms = _keywords(summary)
    scored_rows: list[tuple[int, dict[str, str]]] = []
    repeat_customer = False

    with tickets_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if customer_id and row.get("customer_id") == customer_id:
                repeat_customer = True
            if row["category"] != category:
                continue
            score = len(query_terms & _keywords(row["summary"]))
            if score == 0 and category == "damaged_item":
                score = 1
            scored_rows.append((score, row))

    scored_rows.sort(key=lambda item: item[0], reverse=True)
    top_rows = [row for score, row in scored_rows[:3] if score > 0]
    similar_cases = [
        SimilarCase(
            ticketId=row["ticket_id"],
            summary=row["summary"],
            resolution=row["resolution"],
            refundAmount=float(row["refund_amount"]),
            csat=int(row["csat"]),
        )
        for row in top_rows
    ]

    if not similar_cases:
        return HistoryFinding(
            similarCases=[],
            commonResolution="none found",
            averageRefund=0,
            repeatCustomer=repeat_customer,
            confidence="low",
        )

    common_resolution = Counter(case.resolution for case in similar_cases).most_common(1)[0][0]
    average_refund = round(sum(case.refundAmount for case in similar_cases) / len(similar_cases), 2)
    return HistoryFinding(
        similarCases=similar_cases,
        commonResolution=common_resolution,
        averageRefund=average_refund,
        repeatCustomer=repeat_customer,
        confidence="high" if len(similar_cases) >= 3 else "medium",
    )


def _keywords(value: str) -> set[str]:
    stop_words = {"the", "and", "with", "from", "that", "this", "order", "arrived", "customer"}
    return {word for word in re.findall(r"[a-z0-9]+", value.lower()) if len(word) > 2 and word not in stop_words}


def _not_found(order_id: str | None) -> OrderDetails:
    return OrderDetails(
        orderId=order_id,
        customerId=None,
        customer=None,
        item=None,
        amount=None,
        orderDate=None,
        deliveryDate=None,
        status=None,
        paymentMethod=None,
        daysSinceDelivery=None,
        found=False,
    )
