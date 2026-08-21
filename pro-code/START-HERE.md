# Pro-code start here

This is the starting point for rebuilding the same Contoso complaint-resolution system in code using **Microsoft Agent Framework** with Foundry-hosted agents.

The goal is not to create a different application. The goal is to reproduce the [no-code Foundry portal lab](../LAB-contoso-agent-workflow_Version3.md) in code so learners can compare:

- portal-built agents vs code-built agents,
- visual workflow designer vs code orchestration,
- manual node mapping vs typed contracts,
- portal trace vs local logs/tests.

## Contents

- [Prerequisites](#prerequisites)
- [Foundry-first data model](#foundry-first-data-model)
- [Upload the seed data](#upload-the-seed-data)
- [Included data](#included-data)
- [Iteration 1 — Grounded Advisor in code](#iteration-1--grounded-advisor-in-code)
- [Iteration 2 — First Workflow in code](#iteration-2--first-workflow-in-code)
- [Iteration 3 — Full System in code](#iteration-3--full-system-in-code)
- [Testing contracts](#testing-contracts)
- [Build rule](#build-rule)

## Prerequisites

- Python 3.11+ or 3.12+
- Access to a Microsoft Foundry project
- Deployed models matching the [portal lab setup](../LAB-contoso-agent-workflow_Version3.md#two-step-exercise):
  - small/fast model, for example `gpt-4o-mini`
  - large/judgement model, for example `gpt-4o`
- The preloaded simulated seed data in [`../data/`](../data/)

Install dependencies:

```bash
cd pro-code
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

Configure environment values:

```bash
cp .env.example .env
# edit .env with your Foundry project endpoint, knowledge base, deployments, and tool names
```

> The Microsoft Agent Framework Python package is `agent-framework`, and the Foundry provider package is `agent-framework-foundry`.

## Foundry-first data model

The pro-code track is intentionally **not** a local CSV application.

The files in [`../data/`](../data/) are seed assets for the workshop. In a real project, those facts would live in enterprise systems and be accessed through Foundry IQ, Foundry Agent knowledge, Foundry tools, Logic Apps, MCP servers, APIs, or approved data connectors.

Runtime rule:

> Agent code must not answer business questions by reading `orders.csv`, `past-tickets.csv`, or policy files directly from the repo. Upload the files to Foundry IQ / agent knowledge or expose them through Foundry tools, then call those agents/tools from code.

The only local data helper left in the code parses [`sample-complaints.md`](../data/sample-complaints.md) so learners can run test inputs by number.

## Upload the seed data

Use these files as upload/setup inputs:

| Seed file | Recommended Foundry use |
|---|---|
| [`returns-policy.md`](../data/returns-policy.md) | Foundry IQ / agent knowledge for the Policy Agent |
| [`tone-of-voice.md`](../data/tone-of-voice.md) | Foundry IQ / agent knowledge for the Response Writer Agent |
| [`orders.csv`](../data/orders.csv) | Foundry tool or Foundry IQ-backed order lookup tool |
| [`past-tickets.csv`](../data/past-tickets.csv) | Foundry tool or Foundry IQ-backed history search tool |
| [`sample-complaints.md`](../data/sample-complaints.md) | Local test input file only |

Validate the local seed files before uploading:

```bash
python -m contoso_lab.main validate-data
```

## Included data

The repo already includes the fabricated Contoso lab data in [`../data/`](../data/). See [`../data/README.md`](../data/README.md) for file-by-file usage.

- [`returns-policy.md`](../data/returns-policy.md)
- [`tone-of-voice.md`](../data/tone-of-voice.md)
- [`sample-complaints.md`](../data/sample-complaints.md)
- [`orders.csv`](../data/orders.csv)
- [`past-tickets.csv`](../data/past-tickets.csv)

Use these to configure Foundry IQ / Foundry tools. Do not treat them as runtime databases in the pro-code implementation.

## Iteration 1 — Grounded Advisor in code

Portal equivalent: [Iteration 1 — The Grounded Advisor](../LAB-contoso-agent-workflow_Version3.md#iteration-1--the-grounded-advisor).

Code entry point:

- [`src/contoso_lab/iteration1_grounded_advisor.py`](./src/contoso_lab/iteration1_grounded_advisor.py)

Prompt file:

- [`prompts/complaint_advisor.md`](./prompts/complaint_advisor.md)

Knowledge source setup:

- Upload [`returns-policy.md`](../data/returns-policy.md) to Foundry IQ / agent knowledge.
- Upload [`tone-of-voice.md`](../data/tone-of-voice.md) to Foundry IQ / agent knowledge.

What to write:

1. Implement the `FoundryAgentClient._run_agent(...)` adapter in [`foundry_client.py`](./src/contoso_lab/foundry_client.py).
2. Create one Foundry-backed Agent Framework agent using the large model.
3. Configure that agent to use the Foundry IQ / knowledge sources above.
4. Send one complaint at a time from [`sample-complaints.md`](../data/sample-complaints.md).
5. Assert that the response includes:
   - `STEP 1 — UNDERSTAND`,
   - `STEP 2 — POLICY VERDICT`,
   - `STEP 3 — DRAFT REPLY`,
   - real clause references where policy applies,
   - `POLICY_UNCLEAR` for unsupported refund methods.

Run after Foundry configuration is complete:

```bash
python -m contoso_lab.main iteration1 --complaint 1
```

## Iteration 2 — First Workflow in code

Portal equivalent: [Iteration 2 — The First Workflow](../LAB-contoso-agent-workflow_Version3.md#iteration-2--the-first-workflow).

```text
Start -> Intake -> Policy -> Response Writer -> Output
```

Code entry point:

- [`src/contoso_lab/iteration2_first_workflow.py`](./src/contoso_lab/iteration2_first_workflow.py)

Prompt files:

- [`prompts/intake_agent.md`](./prompts/intake_agent.md)
- [`prompts/policy_agent.md`](./prompts/policy_agent.md)
- [`prompts/response_writer_agent.md`](./prompts/response_writer_agent.md)

What to write:

1. Implement agent calls in [`FoundryAgentClient`](./src/contoso_lab/foundry_client.py).
2. Validate Intake output against `IntakeResult` in [`models.py`](./src/contoso_lab/models.py).
3. Validate Policy output against `PolicyFinding` in [`models.py`](./src/contoso_lab/models.py).
4. Return `finalReply` as plain text from the Response Writer Agent.

Run after Foundry configuration is complete:

```bash
python -m contoso_lab.main iteration2 --complaint 1
python -m contoso_lab.main iteration2 --complaint 2
python -m contoso_lab.main iteration2 --complaint 3
```

## Iteration 3 — Full System in code

Portal equivalent: [Iteration 3 — The Full System](../LAB-contoso-agent-workflow_Version3.md#iteration-3--the-full-system).

```text
Intake
  ├─ Order Lookup
  ├─ Policy
  └─ History
      ↓
Resolution
  ├─ Human approval, when required
  └─ Response Writer
```

Code entry point:

- [`src/contoso_lab/iteration3_full_system.py`](./src/contoso_lab/iteration3_full_system.py)

Additional prompt files:

- [`prompts/order_lookup_agent.md`](./prompts/order_lookup_agent.md)
- [`prompts/history_agent.md`](./prompts/history_agent.md)
- [`prompts/resolution_agent.md`](./prompts/resolution_agent.md)

What to write:

1. Reuse Intake from [Iteration 2](#iteration-2--first-workflow-in-code).
2. Configure [`orders.csv`](../data/orders.csv) as a Foundry tool or Foundry IQ-backed lookup, then implement `lookup_order(...)` in [`foundry_client.py`](./src/contoso_lab/foundry_client.py).
3. Configure [`past-tickets.csv`](../data/past-tickets.csv) as a Foundry tool or Foundry IQ-backed search, then implement `search_history(...)` in [`foundry_client.py`](./src/contoso_lab/foundry_client.py).
4. Run Order Lookup, Policy, and History concurrently after Intake using `asyncio.gather(...)`.
5. Validate outputs against contracts in [`models.py`](./src/contoso_lab/models.py):
   - `OrderDetails`,
   - `PolicyFinding`,
   - `HistoryFinding`.
6. Pass all upstream JSON objects into Resolution.
7. Route to a human approval Foundry tool when:
   - `recommendation.refundAmount > 200`,
   - `intake.category == "fraud"`,
   - `policyFinding.requiresManagerApproval == true`,
   - later memory indicates a third refund in 12 months.

Run after Foundry configuration is complete:

```bash
python -m contoso_lab.main iteration3 --complaint 1
python -m contoso_lab.main iteration3 --complaint 2 --auto-approve
python -m contoso_lab.main iteration3 --complaint 4 --auto-approve
python -m contoso_lab.main iteration3 --complaint 7
```

## Testing contracts

Start with contract tests before calling live models:

```bash
pytest
```

The tests in [`src/tests/test_contracts.py`](./src/tests/test_contracts.py) focus on stable lab requirements:

- seed data paths resolve from either repo root or `pro-code/`,
- sample complaints parse correctly,
- order IDs and customer IDs can be extracted from test inputs,
- unknown order responses cannot contain fabricated facts,
- high-value refunds require approval,
- fraud complaints require approval,
- no-order complaints ask one clarifying question.

## Build rule

When a test fails, change the smallest possible unit:

- bad category or missing order ID -> [`Intake Agent`](./prompts/intake_agent.md) prompt/code,
- invented order -> [`Order Lookup Agent`](./prompts/order_lookup_agent.md) / Foundry order tool,
- wrong remedy -> [`Policy Agent`](./prompts/policy_agent.md) / Foundry IQ policy grounding,
- bad approval route -> [`Resolution Agent`](./prompts/resolution_agent.md) or routing condition in [`iteration3_full_system.py`](./src/contoso_lab/iteration3_full_system.py),
- wrong tone -> [`Response Writer Agent`](./prompts/response_writer_agent.md) / Foundry IQ tone grounding.
