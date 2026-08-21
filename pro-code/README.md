# Pro-code Contoso Agent Lab

This folder contains the code-first version of the Contoso complaint-resolution lab.

Use [`START-HERE.md`](./START-HERE.md) as the implementation guide.

## Quick links

- [Start the pro-code guide](./START-HERE.md)
- [Prerequisites](./START-HERE.md#prerequisites)
- [Included data](./START-HERE.md#included-data)
- [Iteration 1 — Grounded Advisor in code](./START-HERE.md#iteration-1--grounded-advisor-in-code)
- [Iteration 2 — First Workflow in code](./START-HERE.md#iteration-2--first-workflow-in-code)
- [Iteration 3 — Full System in code](./START-HERE.md#iteration-3--full-system-in-code)
- [Testing contracts](./START-HERE.md#testing-contracts)

## Implementation strategy

- Keep the same iterations as the [portal lab](../LAB-contoso-agent-workflow_Version3.md): [Iteration 1](../LAB-contoso-agent-workflow_Version3.md#iteration-1--the-grounded-advisor), [Iteration 2](../LAB-contoso-agent-workflow_Version3.md#iteration-2--the-first-workflow), and [Iteration 3](../LAB-contoso-agent-workflow_Version3.md#iteration-3--the-full-system).
- Keep each agent prompt in [`prompts/`](./prompts/).
- Keep typed JSON contracts in [`src/contoso_lab/models.py`](./src/contoso_lab/models.py).
- Keep orchestration code separated by iteration:
  - [`iteration1_grounded_advisor.py`](./src/contoso_lab/iteration1_grounded_advisor.py)
  - [`iteration2_first_workflow.py`](./src/contoso_lab/iteration2_first_workflow.py)
  - [`iteration3_full_system.py`](./src/contoso_lab/iteration3_full_system.py)
- Keep Data Pack files in [`../data/`](../data/) and see [`../data/README.md`](../data/README.md) for file-by-file usage.

## Status

This is a skeleton. The files mark where to add Microsoft Agent Framework code after you confirm the current SDK APIs for your Foundry-hosted agents. Start with [`START-HERE.md`](./START-HERE.md#contents), then implement each iteration in order.
