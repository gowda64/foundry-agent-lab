# Data folder

The simulated Contoso Retail Data Pack is preloaded here so learners do not need to copy and paste it from the lab markdown.

## Quick links

- [Data files](#data-files)
- [Where each file is used](#where-each-file-is-used)
- [Back to the main lab README](../README.md)

## Data files

| File | Purpose |
|---|---|
| [`returns-policy.md`](./returns-policy.md) | Grounding document for refund, return, approval, and escalation rules |
| [`tone-of-voice.md`](./tone-of-voice.md) | Customer communication guide for final replies |
| [`sample-complaints.md`](./sample-complaints.md) | Primary test inputs for agent and workflow validation |
| [`orders.csv`](./orders.csv) | Simulated order system data for deterministic order lookup |
| [`past-tickets.csv`](./past-tickets.csv) | Simulated resolved support-ticket history for similarity lookup |

## Where each file is used

| File | Used in |
|---|---|
| [`returns-policy.md`](./returns-policy.md) | [Iteration 1](../LAB-contoso-agent-workflow_Version3.md#iteration-1--the-grounded-advisor), [Iteration 2](../LAB-contoso-agent-workflow_Version3.md#iteration-2--the-first-workflow), [Iteration 3](../LAB-contoso-agent-workflow_Version3.md#iteration-3--the-full-system) |
| [`tone-of-voice.md`](./tone-of-voice.md) | [Iteration 1](../LAB-contoso-agent-workflow_Version3.md#iteration-1--the-grounded-advisor), [Iteration 2](../LAB-contoso-agent-workflow_Version3.md#iteration-2--the-first-workflow), [Iteration 3](../LAB-contoso-agent-workflow_Version3.md#iteration-3--the-full-system) |
| [`sample-complaints.md`](./sample-complaints.md) | Test inputs for [Iteration 1](../LAB-contoso-agent-workflow_Version3.md#gate-1), [Iteration 2](../LAB-contoso-agent-workflow_Version3.md#gate-2), and [Iteration 3](../LAB-contoso-agent-workflow_Version3.md#gate-3) |
| [`orders.csv`](./orders.csv) | [Iteration 3 Order Lookup](../LAB-contoso-agent-workflow_Version3.md#iteration-3-agents) |
| [`past-tickets.csv`](./past-tickets.csv) | [Iteration 3 History Agent](../LAB-contoso-agent-workflow_Version3.md#iteration-3-agents) |

All data is fabricated for the lab and safe to use in demos, tests, and workshops.
