# 🧭 Foundry Agent Lab: From No-Code Agents to Pro-Code Multi-Agent Systems

> Build the same Contoso Retail complaint-resolution system twice: first visually in the **Microsoft Foundry portal**, then in code using **Microsoft Agent Framework** with Foundry-hosted agents.

[![Lab Track](https://img.shields.io/badge/track-no--code%20%2B%20pro--code-blue)](#lab-journey)
[![Iterations](https://img.shields.io/badge/iterations-1%20to%203-purple)](#what-you-will-build)
[![Scenario](https://img.shields.io/badge/scenario-Contoso%20Retail-green)](#business-scenario)

Created using **GitHub Copilot** by **Vishwas Gowda**.

---

## Quick links

- [Why this lab exists](#why-this-lab-exists)
- [Business scenario](#business-scenario)
- [Included simulated data](#included-simulated-data)
- [Lab journey](#lab-journey)
- [What you will build](#what-you-will-build)
  - [Iteration 1 — Grounded Advisor](#iteration-1--grounded-advisor)
  - [Iteration 2 — First Workflow](#iteration-2--first-workflow)
  - [Iteration 3 — Full System](#iteration-3--full-system)
- [Repository layout](#repository-layout)
- [How to use this repo](#how-to-use-this-repo)
- [Success criteria](#success-criteria)
- [Learning outcomes](#learning-outcomes)

---

## Why this lab exists

Most agent demos stop at one impressive prompt. This lab goes further.

You will build a realistic customer-support agent system one iteration at a time, starting with a grounded single agent and ending with a multi-agent workflow that can classify complaints, check policy, look up orders, compare past cases, route approvals, and draft customer replies.

The key idea: **build the same system twice**.

1. **No-code first** — learn the shape of the solution in the Microsoft Foundry portal by following the [portal build lab](./LAB-contoso-agent-workflow_Version3.md).
2. **Pro-code second** — rebuild the same design using Microsoft Agent Framework by following the [pro-code start guide](./pro-code/START-HERE.md).

---

## Business scenario

Contoso Retail receives thousands of customer complaints every week. Today, a human support rep has to:

- read and classify the complaint,
- look up the order,
- check the returns policy,
- search similar past tickets,
- decide the remedy,
- get manager approval for high-value or fraud-risk cases,
- write a customer-friendly response.

This lab automates that flow while keeping humans in control of financial and risky decisions.

---

## Included simulated data

The repo is preloaded with the full fabricated Contoso Data Pack in [`data/`](./data/). See the [data folder guide](./data/README.md) for the full list.

- [`returns-policy.md`](./data/returns-policy.md)
- [`tone-of-voice.md`](./data/tone-of-voice.md)
- [`sample-complaints.md`](./data/sample-complaints.md)
- [`orders.csv`](./data/orders.csv)
- [`past-tickets.csv`](./data/past-tickets.csv)

You can use these files directly in the Foundry portal and in the pro-code implementation. No copy-paste from the lab markdown is required.

---

## Lab journey

| Step | Track | What you build | Start here |
|---|---|---|---|
| **1** | 🧩 No-code Foundry portal | [Iterations 1, 2, and 3](./LAB-contoso-agent-workflow_Version3.md#lab-contents) from the Contoso complaint-resolution lab | [`LAB-contoso-agent-workflow_Version3.md`](./LAB-contoso-agent-workflow_Version3.md) |
| **2** | 💻 Pro-code Microsoft Agent Framework | The same [Iterations 1, 2, and 3](./pro-code/START-HERE.md#contents) using Foundry-hosted agents and code orchestration | [`pro-code/START-HERE.md`](./pro-code/START-HERE.md) |

---

## What you will build

### Iteration 1 — Grounded Advisor

One grounded advisor agent that:

- reads a complaint,
- uses the [returns policy](./data/returns-policy.md) and [tone guide](./data/tone-of-voice.md),
- cites real policy clauses,
- refuses when policy is unclear,
- drafts a customer-facing reply.

```text
Complaint -> Complaint Advisor -> Policy verdict + Draft reply
```

Detailed instructions: [Iteration 1 in the portal lab](./LAB-contoso-agent-workflow_Version3.md#iteration-1--the-grounded-advisor) and [Iteration 1 in the pro-code guide](./pro-code/START-HERE.md#iteration-1--grounded-advisor-in-code).

### Iteration 2 — First Workflow

A three-agent workflow with clean JSON hand-offs:

```text
complaintText -> Intake Agent -> Policy Agent -> Response Writer Agent -> finalReply
```

You learn decomposition, structured outputs, variable mapping, and prompt-level debugging.

Detailed instructions: [Iteration 2 in the portal lab](./LAB-contoso-agent-workflow_Version3.md#iteration-2--the-first-workflow) and [Iteration 2 in the pro-code guide](./pro-code/START-HERE.md#iteration-2--first-workflow-in-code).

### Iteration 3 — Full System

A six-agent workflow with parallel lookups and human approval:

```text
Intake
  ├─ Order Lookup
  ├─ Policy
  └─ History
      ↓
Resolution -> approval condition -> Response Writer
```

You add [order lookup](./data/orders.csv), [similar-ticket history](./data/past-tickets.csv), a resolution decision agent, fan-out/fan-in orchestration, and approval routing for refunds over $200 or suspected fraud.

Detailed instructions: [Iteration 3 in the portal lab](./LAB-contoso-agent-workflow_Version3.md#iteration-3--the-full-system) and [Iteration 3 in the pro-code guide](./pro-code/START-HERE.md#iteration-3--full-system-in-code).

---

## Repository layout

```text
.
├── README.md
├── LAB-contoso-agent-workflow_Version3.md
├── data/
│   ├── README.md
│   ├── returns-policy.md
│   ├── tone-of-voice.md
│   ├── sample-complaints.md
│   ├── orders.csv
│   └── past-tickets.csv
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

---

## How to use this repo

1. Start with the no-code lab: [`LAB-contoso-agent-workflow_Version3.md`](./LAB-contoso-agent-workflow_Version3.md).
2. Use the [preloaded Data Pack](./data/README.md) when creating Foundry portal knowledge sources and running tests.
3. Build [Iteration 1](./LAB-contoso-agent-workflow_Version3.md#iteration-1--the-grounded-advisor), [Iteration 2](./LAB-contoso-agent-workflow_Version3.md#iteration-2--the-first-workflow), and [Iteration 3](./LAB-contoso-agent-workflow_Version3.md#iteration-3--the-full-system) in the Microsoft Foundry portal.
4. Move to the pro-code guide: [`pro-code/START-HERE.md`](./pro-code/START-HERE.md).
5. Implement the same agents, prompts, contracts, tests, and workflow logic using Microsoft Agent Framework.
6. Compare the two versions for quality, debuggability, cost, and maintainability.

---

## Success criteria

By the end of [Iteration 3](./LAB-contoso-agent-workflow_Version3.md#iteration-3--the-full-system), both the no-code and pro-code versions should demonstrate:

- grounded policy answers with real clause references,
- `POLICY_UNCLEAR` instead of invented policy,
- prompt-injection resistance,
- JSON-only hand-offs between specialist agents,
- parallel order, policy, and history lookups,
- manager approval routing for refunds over $200 and fraud cases,
- final replies that follow the [Contoso tone guide](./data/tone-of-voice.md).

---

## Learning outcomes

After completing this lab, you should be able to explain and implement:

- when to use one agent versus multiple specialist agents,
- how to ground an agent in enterprise documents,
- how to design JSON contracts between agents,
- how to fan out parallel agent work and join the results,
- where human approval belongs in an agentic workflow,
- how to move from a [portal-built prototype](./LAB-contoso-agent-workflow_Version3.md) to a [code-first implementation](./pro-code/START-HERE.md).

---

## Author

Created using **GitHub Copilot** by **Vishwas Gowda**.
