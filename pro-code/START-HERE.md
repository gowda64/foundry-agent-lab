# Pro-code start here

This is the starting point for rebuilding the same Contoso complaint-resolution system in code using **Microsoft Agent Framework** with Foundry-hosted agents.

The goal is not to create a different application. The goal is to reproduce the [no-code Foundry portal lab](../LAB-contoso-agent-workflow_Version3.md) in code so learners can compare:

- portal-built agents vs code-built agents,
- visual workflow designer vs code orchestration,
- manual node mapping vs typed contracts,
- portal trace vs local logs/tests.

## Contents

- [Prerequisites](#prerequisites)
- [Local reference implementation](#local-reference-implementation)
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
- The preloaded simulated Data Pack in [`../data/`](../data/)

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
# edit .env with your Foundry project endpoint, deployments, and auth settings
```

> The Microsoft Agent Framework Python package is `agent-framework`. The starter also includes `azure-identity`, because the official Foundry quickstart uses Azure credentials with `FoundryChatClient`.

## Local reference implementation

The pro-code folder now includes a deterministic local reference implementation. This means the commands below run before you connect live Foundry-hosted agents.

Use it to verify:

- data loading,
- JSON contracts,
- routing logic,
- human approval branching,
- response-writing shape.

Then replace the local reference functions with Microsoft Agent Framework calls one agent at a time.

## Included data

The repo already includes the fabricated Contoso lab data in [`../data/`](../data/). See [`../data/README.md`](../data/README.md) for file-by-file usage.

- [`returns-policy.md`](../data/returns-policy.md)
- [`tone-of-voice.md`](../data/tone-of-voice.md)
- [`sample-complaints.md`](../data/sample-complaints.md)
- [`orders.csv`](../data/orders.csv)
- [`past-tickets.csv`](../data/past-tickets.csv)

Use these directly for grounding, tests, local deterministic lookups, and workflow validation.

## Iteration 1 — Grounded Advisor in code

Portal equivalent: [Iteration 1 — The Grounded Advisor](../LAB-contoso-agent-workflow_Version3.md#iteration-1--the-grounded-advisor).

Code entry point:

- [`src/contoso_lab/iteration1_grounded_advisor.py`](./src/contoso_lab/iteration1_grounded_advisor.py)

Prompt file:

- [`prompts/complaint_advisor.md`](./prompts/complaint_advisor.md)

Data files:

- [`../data/returns-policy.md`](../data/returns-policy.md)
- [`../data/tone-of-voice.md`](../data/tone-of-voice.md)
- [`../data/sample-complaints.md`](../data/sample-complaints.md)

What to write:

1. Start from the local reference implementation in [`iteration1_grounded_advisor.py`](./src/contoso_lab/iteration1_grounded_advisor.py).
2. Replace the deterministic advisor logic with one Foundry-backed Agent Framework agent using the large model.
3. Load the [returns policy](../data/returns-policy.md) and [tone guide](../data/tone-of-voice.md), or inject their contents into the retrieval/grounding setup supported by your Foundry-hosted agent configuration.
4. Send one complaint at a time from [`sample-complaints.md`](../data/sample-complaints.md).
5. Assert that the response includes:
   - `STEP 1 — UNDERSTAND`,
   - `STEP 2 — POLICY VERDICT`,
   - `STEP 3 — DRAFT REPLY`,
   - real clause references where policy applies,
   - `POLICY_UNCLEAR` for unsupported refund methods.

Run:

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

1. Start from `run_intake(complaint_text)` in [`iteration2_first_workflow.py`](./src/contoso_lab/iteration2_first_workflow.py), then replace it with the Intake Agent call.
2. Validate the Intake output against `IntakeResult` in [`models.py`](./src/contoso_lab/models.py).
3. Replace `run_policy(intake)` with the Policy Agent call.
4. Validate the Policy output against `PolicyFinding` in [`models.py`](./src/contoso_lab/models.py).
5. Replace `run_response_writer(intake, policy_finding)` with the Response Writer Agent call.
6. Return `finalReply` as plain text.

Run:

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
2. Run Order Lookup, Policy, and History concurrently after Intake.
   - In Python, this usually means `asyncio.gather(...)`.
   - In Microsoft Agent Framework, use the framework's concurrent workflow pattern if available in the current SDK.
3. Validate outputs against contracts in [`models.py`](./src/contoso_lab/models.py):
   - `OrderDetails`,
   - `PolicyFinding`,
   - `HistoryFinding`.
4. Pass all upstream JSON objects into Resolution.
5. Route to a human approval function when:
   - `recommendation.refundAmount > 200`,
   - `intake.category == "fraud"`,
   - `policyFinding.requiresManagerApproval == true`,
   - later memory indicates a third refund in 12 months.
6. Pass the final approved/declined/modified decision into Response Writer.

Run:

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

- data paths resolve from either repo root or `pro-code/`,
- sample complaints parse correctly,
- known and unknown orders are handled deterministically,
- high-value refunds require approval,
- fraud complaints require approval,
- no-order complaints ask one clarifying question.

## Build rule

When a test fails, change the smallest possible unit:

- bad category or missing order ID -> [`Intake Agent`](./prompts/intake_agent.md) prompt/code,
- invented order -> [`Order Lookup Agent`](./prompts/order_lookup_agent.md) prompt/code,
- wrong remedy -> [`Policy Agent`](./prompts/policy_agent.md) prompt/code,
- bad approval route -> [`Resolution Agent`](./prompts/resolution_agent.md) or routing condition in [`iteration3_full_system.py`](./src/contoso_lab/iteration3_full_system.py),
- wrong tone -> [`Response Writer Agent`](./prompts/response_writer_agent.md).
