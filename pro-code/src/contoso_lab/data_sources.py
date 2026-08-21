from __future__ import annotations

import re
from pathlib import Path

_COMPLAINT_HEADING = re.compile(r"^###\s+(?P<number>\d+)\s+—\s+(?P<title>.+)$")
_CUSTOMER_ID = re.compile(r"^customerId:\s*(?P<customer_id>\S+)\s*$")
_QUOTED_BLOCK = re.compile(r'"(?P<text>.*)"', re.DOTALL)

REQUIRED_SEED_FILES = [
    "returns-policy.md",
    "tone-of-voice.md",
    "sample-complaints.md",
    "orders.csv",
    "past-tickets.csv",
]


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing required lab file: {path}")
    return path.read_text(encoding="utf-8")


def validate_seed_data_files(data_dir: Path) -> list[Path]:
    """Validate that local seed files exist for upload to Foundry IQ / tools.

    These files are not treated as runtime databases. They are workshop seed
    assets that learners upload to Foundry IQ or use to configure Foundry tools.
    """
    missing = [data_dir / name for name in REQUIRED_SEED_FILES if not (data_dir / name).exists()]
    if missing:
        missing_list = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(f"Missing seed data files:\n{missing_list}")
    return [data_dir / name for name in REQUIRED_SEED_FILES]


def load_sample_complaints(data_dir: Path) -> dict[str, str]:
    """Parse data/sample-complaints.md into complaint text keyed by case number.

    This parser is intentionally the only local data reader used by the runtime.
    It supplies user test inputs. Business lookups should happen through Foundry
    IQ and Foundry tools.
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
