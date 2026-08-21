from __future__ import annotations

from typing import Any, Protocol

from .config import Settings
from .errors import require_configured
from .models import ApprovalResult, HistoryFinding, IntakeResult, OrderDetails, PolicyFinding, Recommendation


class ContosoFoundryClient(Protocol):
    """Boundary between lab orchestration code and Foundry-hosted agents/tools."""

    async def run_intake(self, complaint_text: str) -> IntakeResult: ...

    async def run_policy(self, intake: IntakeResult) -> PolicyFinding: ...

    async def write_response(
        self,
        intake: IntakeResult,
        policy_finding: PolicyFinding,
        order_details: OrderDetails | None = None,
        recommendation: Recommendation | None = None,
    ) -> str: ...

    async def lookup_order(self, order_id: str | None) -> OrderDetails: ...

    async def search_history(self, intake: IntakeResult, customer_id: str | None) -> HistoryFinding: ...

    async def resolve(
        self,
        intake: IntakeResult,
        order_details: OrderDetails,
        policy_finding: PolicyFinding,
        history: HistoryFinding,
    ) -> Recommendation: ...

    async def request_approval(self, recommendation: Recommendation, order_details: OrderDetails) -> ApprovalResult: ...


class FoundryAgentClient:
    """Adapter placeholder for Microsoft Agent Framework + Foundry-hosted agents.

    This class is deliberately the only place that should know about Foundry SDK
    details. The workshop asks learners to replace the TODOs with real calls to:

    - Foundry-hosted agents built with Microsoft Agent Framework,
    - Foundry IQ / knowledge bases for policy, tone, orders, and history,
    - Foundry tools for operational lookups and human approval.

    The methods currently validate configuration and raise clear TODO errors so
    the orchestration code never falls back to local CSV lookup.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.project_endpoint = require_configured(settings.foundry_project_endpoint, "FOUNDRY_PROJECT_ENDPOINT")
        self.knowledge_base = settings.foundry_iq_knowledge_base_id or settings.foundry_iq_knowledge_base_name

    async def run_intake(self, complaint_text: str) -> IntakeResult:
        raw = await self._run_agent(
            agent_name="Intake Agent",
            model_deployment=self.settings.small_model_deployment,
            instructions_file="intake_agent.md",
            payload={"complaintText": complaint_text},
        )
        return IntakeResult.model_validate(raw)

    async def run_policy(self, intake: IntakeResult) -> PolicyFinding:
        raw = await self._run_agent(
            agent_name="Policy Agent",
            model_deployment=self.settings.small_model_deployment,
            instructions_file="policy_agent.md",
            payload={
                "category": intake.category,
                "summary": intake.summary,
                "knowledgeBase": self.knowledge_base,
                "requiredSource": "returns-policy.md",
            },
        )
        return PolicyFinding.model_validate(raw)

    async def write_response(
        self,
        intake: IntakeResult,
        policy_finding: PolicyFinding,
        order_details: OrderDetails | None = None,
        recommendation: Recommendation | None = None,
    ) -> str:
        raw = await self._run_agent(
            agent_name="Response Writer Agent",
            model_deployment=self.settings.large_model_deployment,
            instructions_file="response_writer_agent.md",
            payload={
                "intake": intake.model_dump(),
                "policyFinding": policy_finding.model_dump(),
                "orderDetails": order_details.model_dump() if order_details else None,
                "recommendation": recommendation.model_dump() if recommendation else None,
                "knowledgeBase": self.knowledge_base,
                "requiredSource": "tone-of-voice.md",
            },
        )
        if not isinstance(raw, str):
            raise TypeError("Response Writer Agent must return plain text")
        return raw

    async def lookup_order(self, order_id: str | None) -> OrderDetails:
        raw = await self._call_foundry_tool(
            tool_name=self.settings.order_lookup_tool_name,
            arguments={"orderId": order_id},
            source_hint="orders.csv should be uploaded to Foundry IQ or exposed through this Foundry tool.",
        )
        return OrderDetails.model_validate(raw)

    async def search_history(self, intake: IntakeResult, customer_id: str | None) -> HistoryFinding:
        raw = await self._call_foundry_tool(
            tool_name=self.settings.history_search_tool_name,
            arguments={
                "category": intake.category,
                "summary": intake.summary,
                "customerId": customer_id,
            },
            source_hint="past-tickets.csv should be uploaded to Foundry IQ or exposed through this Foundry tool.",
        )
        return HistoryFinding.model_validate(raw)

    async def resolve(
        self,
        intake: IntakeResult,
        order_details: OrderDetails,
        policy_finding: PolicyFinding,
        history: HistoryFinding,
    ) -> Recommendation:
        raw = await self._run_agent(
            agent_name="Resolution Agent",
            model_deployment=self.settings.large_model_deployment,
            instructions_file="resolution_agent.md",
            payload={
                "intake": intake.model_dump(),
                "orderDetails": order_details.model_dump(),
                "policyFinding": policy_finding.model_dump(),
                "history": history.model_dump(),
            },
        )
        return Recommendation.model_validate(raw)

    async def request_approval(self, recommendation: Recommendation, order_details: OrderDetails) -> ApprovalResult:
        raw = await self._call_foundry_tool(
            tool_name="human-approval",
            arguments={
                "recommendation": recommendation.model_dump(),
                "orderDetails": order_details.model_dump(),
            },
            source_hint="Wire this to your workshop approval channel, Logic App, Teams approval, or equivalent Foundry tool.",
        )
        return ApprovalResult.model_validate(raw)

    async def _run_agent(
        self,
        agent_name: str,
        model_deployment: str,
        instructions_file: str,
        payload: dict[str, Any],
    ) -> Any:
        _ = (agent_name, model_deployment, instructions_file, payload)
        raise NotImplementedError(
            "TODO: create or call the Foundry-hosted Agent Framework agent here. "
            f"Agent: {agent_name}; instructions: pro-code/prompts/{instructions_file}; "
            f"project endpoint: {self.project_endpoint}."
        )

    async def _call_foundry_tool(self, tool_name: str, arguments: dict[str, Any], source_hint: str) -> Any:
        _ = (tool_name, arguments, source_hint)
        raise NotImplementedError(
            "TODO: call the registered Foundry tool here. "
            f"Tool: {tool_name}. {source_hint} Do not read repo CSV files at runtime."
        )
