---
name: feature-implementation-main-mcv
description: Workflow command scaffold for feature-implementation-main-mcv in mcv-parser.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /feature-implementation-main-mcv

Use this workflow when working on **feature-implementation-main-mcv** in `mcv-parser`.

## Goal

Implements a new feature or enhancement that requires changes to both main.py and mcv.py, often with supporting changes in configuration or dependencies.

## Common Files

- `main.py`
- `mcv.py`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Edit main.py to add or update CLI/entry logic.
- Edit mcv.py to implement or adjust core functionality.
- Optionally update dependencies or supporting files (e.g., pyproject.toml, poetry.lock, .gitignore).

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.