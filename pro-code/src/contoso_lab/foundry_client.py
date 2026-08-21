from __future__ import annotations

import json
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

from .config import Settings
from .errors import require_configured
from .models import ApprovalResult, HistoryFinding, IntakeResult, OrderDetails, PolicyFinding, Recommendation

TModel = TypeVar("TModel", bound=BaseModel)


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

    Keep all SDK-specific code in this file. The iteration files should remain
    orchestration-only so the lab clearly separates:

    - agent contracts: models.py
    - agent/tool transport: foundry_client.py
    - workflow shape: iteration1/2/3 files

    Helpful references while filling in TODOs:

    - Microsoft Learn — Foundry provider:
      https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/microsoft-foundry
    - Microsoft Learn — Tools overview:
      https://learn.microsoft.com/en-us/agent-framework/agents/tools/
    - Python samples:
      https://github.com/microsoft/agent-framework/tree/main/python/samples/01-get-started
    - First Foundry agent sample:
      https://github.com/microsoft/agent-framework/blob/main/python/samples/01-get-started/01_hello_agent.py
    - Function tool sample:
      https://github.com/microsoft/agent-framework/blob/main/python/samples/01-get-started/02_add_tools.py
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.project_endpoint = require_configured(settings.foundry_project_endpoint, "FOUNDRY_PROJECT_ENDPOINT")
        self.knowledge_base = settings.foundry_iq_knowledge_base_id or settings.foundry_iq_knowledge_base_name

    async def run_intake(self, complaint_text: str) -> IntakeResult:
        """Call the Intake Agent and validate the JSON contract."""
        raw = await self._run_agent(
            agent_name="Intake Agent",
            model_deployment=self.settings.small_model_deployment,
            instructions_file="intake_agent.md",
            payload={"complaintText": complaint_text},
            expected_shape="IntakeResult JSON only; no markdown fences; no prose.",
        )
        return self._validate_json_contract(raw, IntakeResult, "Intake Agent")

    async def run_policy(self, intake: IntakeResult) -> PolicyFinding:
        """Call the Policy Agent grounded in Foundry IQ / agent knowledge."""
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
            expected_shape="PolicyFinding JSON only, with exact clause text from returns-policy.md.",
        )
        return self._validate_json_contract(raw, PolicyFinding, "Policy Agent")

    async def write_response(
        self,
        intake: IntakeResult,
        policy_finding: PolicyFinding,
        order_details: OrderDetails | None = None,
        recommendation: Recommendation | None = None,
    ) -> str:
        """Call the Response Writer Agent grounded in the tone guide."""
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
            expected_shape="Plain customer-facing email text, 120-180 words, no internal references.",
        )
        if not isinstance(raw, str):
            raise TypeError("Response Writer Agent must return plain text")
        return raw

    async def lookup_order(self, order_id: str | None) -> OrderDetails:
        """Call the Foundry order lookup tool.

        TODO:
        1. Upload `data/orders.csv` to a Foundry IQ knowledge base OR expose an
           approved order API through a Foundry tool / MCP server / Logic App.
        2. Implement `_call_foundry_tool(...)` so this method calls that tool.
        3. Ensure unknown order IDs return `found:false` and all business fields
           null. The `OrderDetails` model enforces this.
        """
        raw = await self._call_foundry_tool(
            tool_name=self.settings.order_lookup_tool_name,
            arguments={"orderId": order_id},
            source_hint="orders.csv should be uploaded to Foundry IQ or exposed through this Foundry tool.",
        )
        return self._validate_json_contract(raw, OrderDetails, "Order Lookup Tool")

    async def search_history(self, intake: IntakeResult, customer_id: str | None) -> HistoryFinding:
        """Call the Foundry history search tool.

        TODO:
        1. Upload `data/past-tickets.csv` to Foundry IQ OR expose a support-ticket
           search service through a Foundry tool / MCP server / Logic App.
        2. Return at most 3 similar cases.
        3. Match on category and product type, not on customer name.
        """
        raw = await self._call_foundry_tool(
            tool_name=self.settings.history_search_tool_name,
            arguments={
                "category": intake.category,
                "summary": intake.summary,
                "customerId": customer_id,
            },
            source_hint="past-tickets.csv should be uploaded to Foundry IQ or exposed through this Foundry tool.",
        )
        return self._validate_json_contract(raw, HistoryFinding, "History Search Tool")

    async def resolve(
        self,
        intake: IntakeResult,
        order_details: OrderDetails,
        policy_finding: PolicyFinding,
        history: HistoryFinding,
    ) -> Recommendation:
        """Call the Resolution Agent and validate its recommendation."""
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
            expected_shape="Recommendation JSON only. Never exceed policyFinding.maxAmount.",
        )
        return self._validate_json_contract(raw, Recommendation, "Resolution Agent")

    async def request_approval(self, recommendation: Recommendation, order_details: OrderDetails) -> ApprovalResult:
        """Call the human approval tool.

        TODO:
        1. For the lab, this can be a lightweight Foundry tool that returns
           `{decision: approve|reject|modify, refundAmount?: number, note?: string}`.
        2. In a real project, back this with Teams approvals, Logic Apps, a service
           desk workflow, or another auditable human approval system.
        3. Keep approval mandatory for refunds over $200 and suspected fraud.
        """
        raw = await self._call_foundry_tool(
            tool_name="human-approval",
            arguments={
                "recommendation": recommendation.model_dump(),
                "orderDetails": order_details.model_dump(),
            },
            source_hint="Wire this to your workshop approval channel, Logic App, Teams approval, or equivalent Foundry tool.",
        )
        return self._validate_json_contract(raw, ApprovalResult, "Human Approval Tool")

    async def _run_agent(
        self,
        agent_name: str,
        model_deployment: str,
        instructions_file: str,
        payload: dict[str, Any],
        expected_shape: str,
    ) -> Any:
        """TODO: create or call a Foundry-hosted Agent Framework agent.

        Recommended implementation path for this lab:

        1. Read the prompt:

           instructions = (self.settings.prompts_dir / instructions_file).read_text()

        2. Build a Foundry chat client and Agent:

           from agent_framework import Agent
           from agent_framework.foundry import FoundryChatClient
           from azure.identity import AzureCliCredential

           client = FoundryChatClient(
               project_endpoint=self.project_endpoint,
               model=model_deployment,
               credential=AzureCliCredential(),
           )

           agent = Agent(
               client=client,
               name=agent_name,
               instructions=instructions,
               # Add app-owned tools here if this agent owns any local tools.
               # See 02_add_tools.py in the official samples for `@tool`.
           )

        3. Send a strict payload. For JSON agents, include the expected output shape
           in the user message so the model has no ambiguity:

           message = json.dumps({
               "task": agent_name,
               "expectedOutput": expected_shape,
               "input": payload,
           })

           result = await agent.run(message)

        4. Convert the result to text/dict according to the current SDK response
           shape. Then parse JSON for structured agents:

           text = str(result)
           raw = json.loads(text)
           return raw

        5. If you use service-managed Prompt/Hosted Agents instead of
           app-owned `Agent(client=FoundryChatClient(...))`, keep the public
           method signatures in this adapter the same and swap only this method.

        Do not read `data/orders.csv`, `data/past-tickets.csv`, or policy files as
        runtime databases here. Those files are seed assets for Foundry IQ/tools.
        """
        _ = (agent_name, model_deployment, instructions_file, payload, expected_shape)
        raise NotImplementedError(
            "TODO: wire Microsoft Agent Framework here. See pro-code/START-HERE.md#if-you-get-stuck "
            f"and implement _run_agent for {agent_name}."
        )

    async def _call_foundry_tool(self, tool_name: str, arguments: dict[str, Any], source_hint: str) -> Any:
        """TODO: call a Foundry tool, MCP tool, Logic App, or API connector.

        If you implement app-owned Python tools with Agent Framework, use the
        official function-tool pattern:

            from typing import Annotated
            from agent_framework import tool
            from pydantic import Field

            @tool(approval_mode="never_require")
            def contoso_order_lookup(
                order_id: Annotated[str, Field(description="Order ID, e.g. CR-10432")],
            ) -> dict:
                # In a real project, call the approved order API here.
                ...

        Then attach the tool when creating the agent:

            agent = Agent(..., tools=[contoso_order_lookup])

        For this lab, tools can read from a Foundry IQ-backed source configured in
        the portal. In a real project, tools should front enterprise systems.
        """
        _ = (tool_name, arguments, source_hint)
        raise NotImplementedError(
            "TODO: call the registered Foundry tool here. "
            f"Tool: {tool_name}. {source_hint} Do not read repo CSV files at runtime."
        )

    @staticmethod
    def _validate_json_contract(raw: Any, model: type[TModel], source: str) -> TModel:
        """Validate an agent/tool response against a strict Pydantic contract.

        SDK hint: if `agent.run(...)` returns text, call `json.loads(text)` before
        this method. If it already returns a dict-like payload, pass that directly.
        """
        if isinstance(raw, model):
            return raw
        if isinstance(raw, str):
            raw = json.loads(raw)
        try:
            return model.model_validate(raw)
        except Exception as exc:  # pragma: no cover - error message path
            raise ValueError(f"{source} returned invalid {model.__name__}: {raw}") from exc
