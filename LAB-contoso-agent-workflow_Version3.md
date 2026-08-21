# Build Lab — Contoso Retail Complaint Resolution

## Build a system of agents in the Microsoft Foundry portal, one working version at a time

This is the no-code Foundry portal half of the lab. The repository currently maintains **Iterations 1, 2, and 3** for this exercise.

> The full workshop handout should live in this file. The pro-code half in [`pro-code/START-HERE.md`](./pro-code/START-HERE.md) mirrors the same iterations, agents, data, and tests.

## Two-step exercise

1. **No-code first:** build the system in the Microsoft Foundry portal following this lab.
2. **Pro-code second:** build the same system on Foundry-hosted agents using Microsoft Agent Framework.

---

# Iteration 1 — The Grounded Advisor

## Goal

Create a single `Complaint Advisor` agent that a support rep can paste a complaint into. The agent answers:

- what the policy allows,
- which policy clause applies,
- whether manager approval is required,
- what customer-facing reply should be sent.

## Portal build

1. Agents → **+ New agent**.
2. Name: `Complaint Advisor`.
3. Model: large model deployment, for example `gpt-4o`.
4. Instructions: copy `Complaint Advisor` from the lab prompt pack.
5. Knowledge: upload:
   - `returns-policy.md`
   - `tone-of-voice.md`
6. Test in the playground.

## Gate 1

The agent must:

- answer from the policy document and cite real clause numbers,
- return `POLICY_UNCLEAR` when the policy is silent,
- ignore prompt-injection attempts in the complaint text,
- produce a 120–180 word reply that follows the tone guide.

---

# Iteration 2 — The First Workflow

## Goal

Split the single agent into three specialist agents and chain them in a workflow.

```text
complaintText -> Intake Agent -> Policy Agent -> Response Writer Agent -> finalReply
```

## Agents

| Agent | Model | Knowledge | Purpose |
|---|---|---|---|
| `Intake Agent` | small | none | classify complaint and extract order ID |
| `Policy Agent` | small | `returns-policy.md` | decide what the policy permits |
| `Response Writer Agent` | large | `tone-of-voice.md` | draft final customer reply |

## Workflow variables

| Variable | Type | Written by |
|---|---|---|
| `complaintText` | string | input |
| `intake` | object | Intake |
| `policyFinding` | object | Policy |
| `finalReply` | string | Response Writer |

## Gate 2

The workflow must:

- run end-to-end on complaints 1, 2, 3, and 6,
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

## Agents

| Agent | Model | Knowledge | Purpose |
|---|---|---|---|
| `Intake Agent` | small | none | classify and extract |
| `Order Lookup Agent` | small | `orders.csv` | retrieve order facts only |
| `Policy Agent` | small | `returns-policy.md` | determine permitted remedy |
| `History Agent` | small | `past-tickets.csv` | find similar resolved cases |
| `Resolution Agent` | large | none | recommend action and approval flag |
| `Response Writer Agent` | large | `tone-of-voice.md` | write final reply |

## Parallel fan-out

After Intake, connect the same Intake output to all three lookup branches:

- Order Lookup
- Policy
- History

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
- halt at the Human node for complaint 2 and complaint 4,
- avoid refunding missing or fabricated orders,
- produce a customer reply that never mentions internal agents, clauses, or approval steps.

---

# Data Pack files

Copy the data pack into [`data/`](./data/):

- `returns-policy.md`
- `tone-of-voice.md`
- `sample-complaints.md`
- `orders.csv`
- `past-tickets.csv`

# Prompt Pack

Copy the agent instructions from the original lab handout into [`pro-code/prompts/`](./pro-code/prompts/) so the portal and pro-code versions use the same prompts.
