# Pro-code start here

This is the starting point for rebuilding the same Contoso complaint-resolution system in code using **Microsoft Agent Framework** with Foundry-hosted agents.

The goal is not to create a different application. The goal is to reproduce the no-code Foundry portal lab in code so learners can compare:

- portal-built agents vs code-built agents,
- visual workflow designer vs code orchestration,
- manual node mapping vs typed contracts,
- portal trace vs local logs/tests.

## Prerequisites

- Python 3.11+ or 3.12+
- Access to a Microsoft Foundry project
- Deployed models matching the lab:
  - small/fast model, for example `gpt-4o-mini`
  - large/judgement model, for example `gpt-4o`
- Local copies of the Data Pack in `../data/`

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

> The Microsoft Agent Framework Python package is `agent-framework`. Check the current Microsoft Agent Framework docs for exact Foundry provider APIs before replacing the TODO blocks.

## Iteration 1 — Grounded Advisor in code

Portal equivalent: one `Complaint Advisor` agent.

Code entry point:

- [`src/contoso_lab/iteration1_grounded_advisor.py`](./src/contoso_lab/iteration1_grounded_advisor.py)

Prompt file:

- [`prompts/complaint_advisor.md`](./prompts/complaint_advisor.md)

Data files:

- `../data/returns-policy.md`
- `../data/tone-of-voice.md`
- `../data/sample-complaints.md`

What to write:

1. Create one Foundry-backed Agent Framework agent using the large model.
2. Load the two knowledge files or inject their contents into the retrieval/grounding setup supported by your Foundry-hosted agent configuration.
3. Send one complaint at a time.
4. Assert that the response includes:
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

Portal equivalent:

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

1. Implement `run_intake(complaint_text)`.
2. Validate the Intake output against `IntakeResult` in [`models.py`](./src/contoso_lab/models.py).
3. Implement `run_policy(intake)`.
4. Validate the Policy output against `PolicyFinding`.
5. Implement `run_response_writer(intake, policy_finding)`.
6. Return `finalReply` as plain text.

Run:

```bash
python -m contoso_lab.main iteration2 --complaint 1
python -m contoso_lab.main iteration2 --complaint 2
python -m contoso_lab.main iteration2 --complaint 3
```

## Iteration 3 — Full System in code

Portal equivalent:

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

1. Reuse Intake from Iteration 2.
2. Run Order Lookup, Policy, and History concurrently after Intake.
   - In Python, this usually means `asyncio.gather(...)`.
   - In Microsoft Agent Framework, use the framework's concurrent workflow pattern if available in the current SDK.
3. Validate outputs against:
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
python -m contoso_lab.main iteration3 --complaint 2
python -m contoso_lab.main iteration3 --complaint 4
python -m contoso_lab.main iteration3 --complaint 7
```

## Testing contracts

Start with contract tests before calling live models:

```bash
pytest
```

The tests focus on stable lab requirements:

- JSON outputs parse correctly,
- high-value refunds require approval,
- fraud complaints require approval,
- no-order complaints ask one clarifying question.

## Build rule

When a test fails, change the smallest possible unit:

- bad category or missing order ID -> Intake prompt/code,
- invented order -> Order Lookup prompt/code,
- wrong remedy -> Policy prompt/code,
- bad approval route -> Resolution or routing condition,
- wrong tone -> Response Writer prompt.
