# 🧭 Foundry Agent Lab: From No-Code Agents to Pro-Code Multi-Agent Systems

> Build the same Contoso Retail complaint-resolution system twice: first visually in the **Microsoft Foundry portal**, then in code using **Microsoft Agent Framework** with Foundry-hosted agents.

[![Lab Track](https://img.shields.io/badge/track-no--code%20%2B%20pro--code-blue)](#lab-journey)
[![Iterations](https://img.shields.io/badge/iterations-1%20to%203-purple)](#what-you-will-build)
[![Scenario](https://img.shields.io/badge/scenario-Contoso%20Retail-green)](#business-scenario)
[![Microsoft Foundry](https://img.shields.io/badge/Microsoft-Foundry-0078D4)](#technologies-you-will-learn)
[![Agent Framework](https://img.shields.io/badge/Microsoft-Agent%20Framework-5C2D91)](#technologies-you-will-learn)
[![Foundry IQ](https://img.shields.io/badge/Foundry-IQ-0B6E69)](#technologies-you-will-learn)
[![Foundry Tools](https://img.shields.io/badge/Foundry-Tools-FFB900)](#technologies-you-will-learn)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)](#technologies-you-will-learn)
[![Pydantic](https://img.shields.io/badge/Pydantic-typed%20contracts-E92063)](#technologies-you-will-learn)
[![Human in the loop](https://img.shields.io/badge/Human--in--the--loop-approval%20gates-D83B01)](#technologies-you-will-learn)
[![GitHub Copilot](https://img.shields.io/badge/Built%20with-GitHub%20Copilot-181717)](#author)

Created using **GitHub Copilot** by **Vishwas Gowda**.

---

## Quick links

- [Why this lab exists](#why-this-lab-exists)
- [Business scenario](#business-scenario)
- [Technologies you will learn](#technologies-you-will-learn)
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

## Technologies you will learn

| Technology / concept | Where it shows up in the lab | Why it matters |
|---|---|---|
| **Microsoft Foundry portal** | [No-code build lab](./LAB-contoso-agent-workflow_Version3.md) | Build, test, trace, and iterate agents visually before writing code. |
| **Microsoft Agent Framework** | [Pro-code guide](./pro-code/START-HERE.md) | Rebuild the same system with code-first agents and orchestration. |
| **Foundry-hosted agents** | [Pro-code implementation map](./pro-code/START-HERE.md#implementation-map) | Run specialist agents backed by deployed Foundry models. |
| **Foundry IQ / agent knowledge** | [Foundry-first data model](./pro-code/START-HERE.md#foundry-first-data-model) | Ground agents in policy, tone, order, and history seed data without using repo files as runtime databases. |
| **Foundry tools** | [Iteration 3 pro-code guide](./pro-code/START-HERE.md#iteration-3--full-system-in-code) | Simulate real operational lookups such as orders, ticket history, and approval workflows. |
| **Multi-agent workflow design** | [What you will build](#what-you-will-build) | Split work across Intake, Policy, Order Lookup, History, Resolution, and Response Writer agents. |
| **Fan-out / fan-in orchestration** | [Iteration 3](#iteration-3--full-system) | Run order, policy, and history lookups in parallel, then join them for a decision. |
| **Human-in-the-loop approval** | [Success criteria](#success-criteria) | Keep humans in control of financial and fraud-risk decisions. |
| **Prompt-injection resistance** | [Iteration 1](#iteration-1--grounded-advisor) | Treat customer messages as untrusted data and ignore malicious instructions. |
| **Structured JSON contracts** | [`models.py`](./pro-code/src/contoso_lab/models.py) | Make agent hand-offs testable and debuggable. |
| **Pydantic validation** | [`pro-code/src/contoso_lab/models.py`](./pro-code/src/contoso_lab/models.py) | Enforce strict contracts for Intake, Policy, Order, History, Resolution, and Approval outputs. |
| **Python async orchestration** | [`iteration3_full_system.py`](./pro-code/src/contoso_lab/iteration3_full_system.py) | Use concurrent execution patterns for multi-agent workflows. |
| **Azure Identity** | [Pro-code prerequisites](./pro-code/START-HERE.md#prerequisites) | Authenticate code to Foundry resources with Azure credentials. |
| **GitHub Copilot** | [Author](#author) | Use Copilot to scaffold, refine, review, and document the lab. |

---

## Included simulated data

The repo is preloaded with the full fabricated Contoso Data Pack in [`data/`](./data/). See the [data folder guide](./data/README.md) for the full list.

- [`returns-policy.md`](./data/returns-policy.md)
- [`tone-of-voice.md`](./data/tone-of-voice.md)
- [`sample-complaints.md`](./data/sample-complaints.md)
- [`orders.csv`](./data/orders.csv)
- [`past-tickets.csv`](./data/past-tickets.csv)

You can use these files directly in the Foundry portal and as seed assets for the pro-code implementation. No copy-paste from the lab markdown is required.

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

- how to build agents visually in the **Microsoft Foundry portal**,
- how to move from a [portal-built prototype](./LAB-contoso-agent-workflow_Version3.md) to a [code-first implementation](./pro-code/START-HERE.md),
- when to use one agent versus multiple specialist agents,
- how to ground agents using **Foundry IQ** and agent knowledge,
- how to expose operational lookups through **Foundry tools** instead of repo-local files,
- how to orchestrate agents with **Microsoft Agent Framework**,
- how to design strict JSON contracts between agents,
- how to validate agent outputs with **Pydantic**,
- how to use Python async fan-out/fan-in patterns for multi-agent workflows,
- where human approval belongs in an agentic workflow,
- how to test for refusal behaviour, prompt-injection resistance, and no-fabrication rules.

---

## Author

Created using **GitHub Copilot** by **Vishwas Gowda**.
