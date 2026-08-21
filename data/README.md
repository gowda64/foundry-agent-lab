# Data folder

The simulated Contoso Retail Data Pack is preloaded here so learners do not need to copy and paste it from the lab markdown.

## Quick links

- [Data files](#data-files)
- [How these files are used](#how-these-files-are-used)
- [Back to the main lab README](../README.md)

## Data files

| File | Purpose |
|---|---|
| [`returns-policy.md`](./returns-policy.md) | Seed grounding document for refund, return, approval, and escalation rules |
| [`tone-of-voice.md`](./tone-of-voice.md) | Seed grounding document for customer communication style |
| [`sample-complaints.md`](./sample-complaints.md) | Local test inputs for agent and workflow validation |
| [`orders.csv`](./orders.csv) | Seed order-system data for a Foundry IQ-backed or tool-backed order lookup |
| [`past-tickets.csv`](./past-tickets.csv) | Seed support-ticket history for a Foundry IQ-backed or tool-backed history search |

## How these files are used

| File | No-code portal use | Pro-code use |
|---|---|---|
| [`returns-policy.md`](./returns-policy.md) | Upload as knowledge for the [Complaint Advisor](../LAB-contoso-agent-workflow_Version3.md#iteration-1--the-grounded-advisor) and [Policy Agent](../LAB-contoso-agent-workflow_Version3.md#iteration-2--the-first-workflow). | Upload to Foundry IQ / agent knowledge; the pro-code Policy Agent should retrieve it through Foundry, not read it from this repo at runtime. |
| [`tone-of-voice.md`](./tone-of-voice.md) | Upload as knowledge for the [Complaint Advisor](../LAB-contoso-agent-workflow_Version3.md#iteration-1--the-grounded-advisor) and [Response Writer Agent](../LAB-contoso-agent-workflow_Version3.md#iteration-2--the-first-workflow). | Upload to Foundry IQ / agent knowledge; the pro-code Response Writer should retrieve it through Foundry, not read it from this repo at runtime. |
| [`sample-complaints.md`](./sample-complaints.md) | Use as manual playground and workflow test inputs. | Parsed locally only so `--complaint N` can load a test input. This is not business grounding data. |
| [`orders.csv`](./orders.csv) | Upload as knowledge for the portal [Order Lookup Agent](../LAB-contoso-agent-workflow_Version3.md#iteration-3-agents). | Upload to Foundry IQ or expose through a Foundry tool named by `ORDER_LOOKUP_TOOL_NAME`. Do not query the CSV from pro-code runtime logic. |
| [`past-tickets.csv`](./past-tickets.csv) | Upload as knowledge for the portal [History Agent](../LAB-contoso-agent-workflow_Version3.md#iteration-3-agents). | Upload to Foundry IQ or expose through a Foundry tool named by `HISTORY_SEARCH_TOOL_NAME`. Do not query the CSV from pro-code runtime logic. |

All data is fabricated for the lab and safe to use in demos, tests, and workshops.
