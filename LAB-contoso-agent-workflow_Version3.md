# Build Lab — Contoso Retail Complaint Resolution

## Build a system of agents in the Microsoft Foundry portal, one working version at a time

This is the no-code Foundry portal half of the lab. The repository currently maintains **Iterations 1, 2, and 3** for this exercise.

> The pro-code half in [`pro-code/START-HERE.md`](./pro-code/START-HERE.md) mirrors the same iterations, agents, data, and tests using Microsoft Agent Framework, Foundry IQ, and Foundry tools.

## Lab contents

- [Two-step exercise](#two-step-exercise)
- [Preloaded Data Pack](#preloaded-data-pack)
- [Iteration 1 — The Grounded Advisor](#iteration-1--the-grounded-advisor)
  - [Iteration 1 portal build](#iteration-1-portal-build)
  - [Gate 1](#gate-1)
- [Iteration 2 — The First Workflow](#iteration-2--the-first-workflow)
  - [Iteration 2 agents](#iteration-2-agents)
  - [Iteration 2 workflow variables](#iteration-2-workflow-variables)
  - [Gate 2](#gate-2)
- [Iteration 3 — The Full System](#iteration-3--the-full-system)
  - [Iteration 3 agents](#iteration-3-agents)
  - [Parallel fan-out](#parallel-fan-out)
  - [Human approval routing](#human-approval-routing)
  - [Gate 3](#gate-3)
- [Prompt Pack](#prompt-pack)

## Two-step exercise

1. **No-code first:** build the system in the Microsoft Foundry portal following this lab.
2. **Pro-code second:** build the same system on Foundry-hosted agents using Microsoft Agent Framework by following [`pro-code/START-HERE.md`](./pro-code/START-HERE.md).

## Preloaded Data Pack

The simulated data is already available in [`data/`](./data/). See the [data folder guide](./data/README.md) for file-by-file usage.

- [`returns-policy.md`](./data/returns-policy.md)
- [`tone-of-voice.md`](./data/tone-of-voice.md)
- [`sample-complaints.md`](./data/sample-complaints.md)
- [`orders.csv`](./data/orders.csv)
- [`past-tickets.csv`](./data/past-tickets.csv)

Use these files directly when uploading knowledge to Foundry portal agents. In the pro-code track, treat them as seed assets for Foundry IQ / Foundry tools rather than as runtime files read by Python code.

---

# Iteration 1 — The Grounded Advisor

## Goal

Create a single `Complaint Advisor` agent that a support rep can paste a complaint into. The agent answers:

- what the policy allows,
- which policy clause applies,
- whether manager approval is required,
- what customer-facing reply should be sent.

## Iteration 1 portal build

1. Agents → **+ New agent**.
2. Name: `Complaint Advisor`.
3. Model: large model deployment, for example `gpt-4o`.
4. Instructions: use the [`complaint_advisor.md`](./pro-code/prompts/complaint_advisor.md) prompt.
5. Knowledge: upload:
   - [`data/returns-policy.md`](./data/returns-policy.md)
   - [`data/tone-of-voice.md`](./data/tone-of-voice.md)
6. Test in the playground with [`data/sample-complaints.md`](./data/sample-complaints.md).

## Gate 1

The agent must:

- answer from the [policy document](./data/returns-policy.md) and cite real clause numbers,
- return `POLICY_UNCLEAR` when the policy is silent,
- ignore prompt-injection attempts in the [sample complaints](./data/sample-complaints.md),
- produce a 120–180 word reply that follows the [tone guide](./data/tone-of-voice.md).

---

# Iteration 2 — The First Workflow

## Goal

Split the single agent into three specialist agents and chain them in a workflow.

```text
complaintText -> Intake Agent -> Policy Agent -> Response Writer Agent -> finalReply
```

## Iteration 2 agents

| Agent | Model | Knowledge | Prompt | Purpose |
|---|---|---|---|---|
| `Intake Agent` | small | none | [`intake_agent.md`](./pro-code/prompts/intake_agent.md) | classify complaint and extract order ID |
| `Policy Agent` | small | [`data/returns-policy.md`](./data/returns-policy.md) | [`policy_agent.md`](./pro-code/prompts/policy_agent.md) | decide what the policy permits |
| `Response Writer Agent` | large | [`data/tone-of-voice.md`](./data/tone-of-voice.md) | [`response_writer_agent.md`](./pro-code/prompts/response_writer_agent.md) | draft final customer reply |

## Iteration 2 workflow variables

| Variable | Type | Written by |
|---|---|---|
| `complaintText` | string | input |
| `intake` | object | Intake |
| `policyFinding` | object | Policy |
| `finalReply` | string | Response Writer |

## Gate 2

The workflow must:

- run end-to-end on complaints 1, 2, 3, and 6 from [`data/sample-complaints.md`](./data/sample-complaints.md),
- pass clean JSON between agents,
- isolate policy logic from response writing,
- be explainable from the YAML view.

---

# Iteration 3 — The Full System

## Goal

Add order lookup, past-ticket history, a resolution decision, parallel execution, and human approval.

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

## Iteration 3 agents

| Agent | Model | Knowledge | Prompt | Purpose |
|---|---|---|---|---|
| `Intake Agent` | small | none | [`intake_agent.md`](./pro-code/prompts/intake_agent.md) | classify and extract |
| `Order Lookup Agent` | small | [`data/orders.csv`](./data/orders.csv) | [`order_lookup_agent.md`](./pro-code/prompts/order_lookup_agent.md) | retrieve order facts only |
| `Policy Agent` | small | [`data/returns-policy.md`](./data/returns-policy.md) | [`policy_agent.md`](./pro-code/prompts/policy_agent.md) | determine permitted remedy |
| `History Agent` | small | [`data/past-tickets.csv`](./data/past-tickets.csv) | [`history_agent.md`](./pro-code/prompts/history_agent.md) | find similar resolved cases |
| `Resolution Agent` | large | none | [`resolution_agent.md`](./pro-code/prompts/resolution_agent.md) | recommend action and approval flag |
| `Response Writer Agent` | large | [`data/tone-of-voice.md`](./data/tone-of-voice.md) | [`response_writer_agent.md`](./pro-code/prompts/response_writer_agent.md) | write final reply |

## Parallel fan-out

After Intake, connect the same Intake output to all three lookup branches:

- Order Lookup, grounded in [`data/orders.csv`](./data/orders.csv)
- Policy, grounded in [`data/returns-policy.md`](./data/returns-policy.md)
- History, grounded in [`data/past-tickets.csv`](./data/past-tickets.csv)

Do **not** chain them. They should overlap in the trace.

## Human approval routing

Pause for human approval when any of these are true:

- `recommendation.refundAmount > 200`
- `intake.category == "fraud"`
- `policyFinding.requiresManagerApproval == true`
- later memory indicates a third refund in 12 months

## Gate 3

The workflow must:

- run six single-purpose agents,
- execute Order Lookup, Policy, and History concurrently,
- halt at the Human node for complaint 2 and complaint 4 from [`data/sample-complaints.md`](./data/sample-complaints.md),
- avoid refunding missing or fabricated orders from [`data/orders.csv`](./data/orders.csv),
- produce a customer reply that never mentions internal agents, clauses, or approval steps.

---

# Prompt Pack

The portal lab and pro-code lab should use the same prompt text. Prompt files live in [`pro-code/prompts/`](./pro-code/prompts/).

For the code-first version, continue with [`pro-code/START-HERE.md`](./pro-code/START-HERE.md).
