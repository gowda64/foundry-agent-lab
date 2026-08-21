from __future__ import annotations

from .foundry_client import ContosoFoundryClient
from .iteration1_grounded_advisor import default_client
from .models import IntakeResult, OrderDetails, PolicyFinding, Recommendation


async def run_intake(complaint_text: str, client: ContosoFoundryClient | None = None) -> IntakeResult:
    """Run the Intake Agent in Foundry.

    The agent should return JSON matching IntakeResult. Do not resolve the
    complaint or read local data files in this step.
    """
    return await (client or default_client()).run_intake(complaint_text)


async def run_policy(intake: IntakeResult, client: ContosoFoundryClient | None = None) -> PolicyFinding:
    """Run the Policy Agent grounded by Foundry IQ / agent knowledge."""
    return await (client or default_client()).run_policy(intake)


async def run_response_writer(
    intake: IntakeResult,
    policy_finding: PolicyFinding,
    order_details: OrderDetails | None = None,
    recommendation: Recommendation | None = None,
    client: ContosoFoundryClient | None = None,
) -> str:
    """Run the Response Writer Agent grounded by the tone guide in Foundry IQ."""
    return await (client or default_client()).write_response(intake, policy_finding, order_details, recommendation)


async def run_iteration2(complaint_text: str, client: ContosoFoundryClient | None = None) -> str:
    active_client = client or default_client()
    intake = await run_intake(complaint_text, active_client)
    policy_finding = await run_policy(intake, active_client)
    return await run_response_writer(intake, policy_finding, client=active_client)
