# 🧭 Foundry Agent Lab: From No-Code Agents to Pro-Code Multi-Agent Systems

> Build the same Contoso Retail complaint-resolution system twice: first visually in the **Microsoft Foundry portal**, then in code using **Microsoft Agent Framework** with Foundry-hosted agents.

[![Lab Track](https://img.shields.io/badge/track-no--code%20%2B%20pro--code-blue)](#lab-journey)
[![Iterations](https://img.shields.io/badge/iterations-1%20to%203-purple)](#what-you-will-build)
[![Scenario](https://img.shields.io/badge/scenario-Contoso%20Retail-green)](#business-scenario)

Created using **GitHub Copilot** by **Vishwas Gowda**.

---

## ✨ Why this lab exists

Most agent demos stop at one impressive prompt. This lab goes further.

You will build a realistic customer-support agent system one iteration at a time, starting with a grounded single agent and ending with a multi-agent workflow that can classify complaints, check policy, look up orders, compare past cases, route approvals, and draft customer replies.

The key idea: **build the same system twice**.

1. **No-code first** — learn the shape of the solution in the Microsoft Foundry portal.
2. **Pro-code second** — rebuild the same design using Microsoft Agent Framework so you understand the implementation model behind the visual workflow.

---

## 🛒 Business scenario

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

## 🚦 Lab journey

| Step | Track | What you build | Start here |
|---|---|---|---|
| **1** | 🧩 No-code Foundry portal | Iterations 1, 2, and 3 from the Contoso complaint-resolution lab | [`LAB-contoso-agent-workflow_Version3.md`](./LAB-contoso-agent-workflow_Version3.md) |
| **2** | 💻 Pro-code Microsoft Agent Framework | The same Iterations 1, 2, and 3 using Foundry-hosted agents and code orchestration | [`pro-code/START-HERE.md`](./pro-code/START-HERE.md) |

---

## 🏗️ What you will build

### Iteration 1 — Grounded Advisor

One grounded advisor agent that:

- reads a complaint,
- uses the returns policy and tone guide,
- cites real policy clauses,
- refuses when policy is unclear,
- drafts a customer-facing reply.

```text
Complaint -> Complaint Advisor -> Policy verdict + Draft reply
```

### Iteration 2 — First Workflow

A three-agent workflow with clean JSON hand-offs:

```text
complaintText -> Intake Agent -> Policy Agent -> Response Writer Agent -> finalReply
```

You learn decomposition, structured outputs, variable mapping, and prompt-level debugging.

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

You add order lookup, similar-ticket history, a resolution decision agent, fan-out/fan-in orchestration, and approval routing for refunds over $200 or suspected fraud.

---

## 📁 Repository layout

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

---

## ▶️ How to use this repo

1. Start with the no-code lab: [`LAB-contoso-agent-workflow_Version3.md`](./LAB-contoso-agent-workflow_Version3.md).
2. Copy the Data Pack from the lab into [`data/`](./data/).
3. Build Iterations 1, 2, and 3 in the Microsoft Foundry portal.
4. Move to the pro-code guide: [`pro-code/START-HERE.md`](./pro-code/START-HERE.md).
5. Implement the same agents, prompts, contracts, tests, and workflow logic using Microsoft Agent Framework.
6. Compare the two versions for quality, debuggability, cost, and maintainability.

---

## ✅ Success criteria

By the end of Iteration 3, both the no-code and pro-code versions should demonstrate:

- grounded policy answers with real clause references,
- `POLICY_UNCLEAR` instead of invented policy,
- prompt-injection resistance,
- JSON-only hand-offs between specialist agents,
- parallel order, policy, and history lookups,
- manager approval routing for refunds over $200 and fraud cases,
- final replies that follow the Contoso tone guide.

---

## 🧠 Learning outcomes

After completing this lab, you should be able to explain and implement:

- when to use one agent versus multiple specialist agents,
- how to ground an agent in enterprise documents,
- how to design JSON contracts between agents,
- how to fan out parallel agent work and join the results,
- where human approval belongs in an agentic workflow,
- how to move from a portal-built prototype to a code-first implementation.

---

## 👤 Author

Created using **GitHub Copilot** by **Vishwas Gowda**.
