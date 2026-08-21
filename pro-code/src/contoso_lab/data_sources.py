from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from .models import OrderDetails


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing required lab data file: {path}")
    return path.read_text(encoding="utf-8")


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
