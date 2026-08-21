from __future__ import annotations

import argparse
import asyncio

from .config import get_settings
from .iteration1_grounded_advisor import run_iteration1
from .iteration2_first_workflow import run_iteration2
from .iteration3_full_system import run_iteration3


def load_complaint_by_number(number: str) -> str:
    """Temporary helper.

    TODO: parse sample-complaints.md into individual cases. Until then, pass complaint text directly
    with --text or implement this parser as part of the exercise.
    """
    settings = get_settings()
    path = settings.data_dir / "sample-complaints.md"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Copy it from the lab Data Pack.")
    raise NotImplementedError("Parse sample-complaints.md and return the requested numbered complaint.")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Contoso Foundry Agent Lab")
    parser.add_argument("iteration", choices=["iteration1", "iteration2", "iteration3"])
    parser.add_argument("--complaint", help="Complaint number from sample-complaints.md")
    parser.add_argument("--text", help="Raw complaint text")
    args = parser.parse_args()

    if args.text:
        complaint_text = args.text
    elif args.complaint:
        complaint_text = load_complaint_by_number(args.complaint)
    else:
        raise SystemExit("Provide --complaint N or --text 'complaint body'")

    if args.iteration == "iteration1":
        result = await run_iteration1(complaint_text)
    elif args.iteration == "iteration2":
        result = await run_iteration2(complaint_text)
    else:
        result = await run_iteration3(complaint_text)

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
