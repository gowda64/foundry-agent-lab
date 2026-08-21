from .models import IntakeResult, PolicyFinding


async def run_intake(complaint_text: str) -> IntakeResult:
    """TODO: call the Intake Agent and parse JSON into IntakeResult."""
    raise NotImplementedError


async def run_policy(intake: IntakeResult) -> PolicyFinding:
    """TODO: call the Policy Agent using intake.category and intake.summary."""
    raise NotImplementedError


async def run_response_writer(intake: IntakeResult, policy_finding: PolicyFinding) -> str:
    """TODO: call the Response Writer Agent and return finalReply."""
    raise NotImplementedError


async def run_iteration2(complaint_text: str) -> str:
    intake = await run_intake(complaint_text)
    policy_finding = await run_policy(intake)
    return await run_response_writer(intake, policy_finding)
