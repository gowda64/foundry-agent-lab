# Foundry Agent Lab

Two-half onboarding lab for building the same Contoso Retail complaint-resolution multi-agent system twice:

1. **No-code** in the Microsoft Foundry portal by following the build lab.
2. **Pro-code** on Foundry-hosted agents using Microsoft Agent Framework.

The exercise intentionally keeps the same business problem, data pack, agent responsibilities, and test cases across both halves so learners can compare portal orchestration with code-first orchestration.

## Lab flow

| Step | Track | What you build | Start here |
|---|---|---|---|
| 1 | No-code Foundry portal | Iterations 1, 2, and 3 from the Contoso complaint-resolution lab | [`LAB-contoso-agent-workflow_Version3.md`](./LAB-contoso-agent-workflow_Version3.md) |
| 2 | Pro-code Microsoft Agent Framework | The same Iterations 1, 2, and 3 using Foundry-hosted agents and code orchestration | [`pro-code/START-HERE.md`](./pro-code/START-HERE.md) |

## What we will build

### Iteration 1 — Grounded Advisor

A single grounded advisor agent that:

- reads a complaint,
- uses the returns policy and tone guide,
- cites real policy clauses,
- refuses when policy is unclear,
- drafts a customer-facing reply.

### Iteration 2 — First Workflow

A three-agent workflow:

```text
complaintText -> Intake Agent -> Policy Agent -> Response Writer Agent -> finalReply
```

This teaches decomposition, structured JSON hand-offs, variable mapping, and debuggable prompts.

### Iteration 3 — Full System

A six-agent workflow with fan-out/fan-in and human approval:

```text
Intake
  ├─ Order Lookup
  ├─ Policy
  └─ History
      ↓
Resolution -> approval condition -> Response Writer
```

This adds order lookup, similar-ticket history, a resolution decision agent, parallel branches, and manager approval for financial or fraud-risk cases.

## Repository layout

```text
.
├── README.md
├── LAB-contoso-agent-workflow_Version3.md
├── data/
│   └── README.md
└── pro-code/
    ├── START-HERE.md
    ├── README.md
    ├── pyproject.toml
    ├── requirements.txt
    ├── .env.example
    ├── prompts/
    └── src/
        └── contoso_lab/
```

## How to use this repo

1. Complete the no-code version first by following [`LAB-contoso-agent-workflow_Version3.md`](./LAB-contoso-agent-workflow_Version3.md).
2. Copy the Data Pack from the lab into `data/`.
3. Follow [`pro-code/START-HERE.md`](./pro-code/START-HERE.md) to implement the same system in Microsoft Agent Framework.
4. Keep the portal and code versions aligned by using the same prompts, test complaints, policy file, order data, and expected routing gates.

## Success criteria

By the end of Iteration 3, both the portal and pro-code versions should demonstrate:

- grounded policy answers with real clause references,
- `POLICY_UNCLEAR` instead of invented policy,
- prompt-injection resistance,
- JSON-only hand-offs between specialist agents,
- parallel order, policy, and history lookups,
- manager approval routing for refunds over $200 and fraud cases,
- polite final replies that follow the Contoso tone guide.
