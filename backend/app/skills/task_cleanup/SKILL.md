# Task Cleanup Skill

## Purpose

Use this skill when the user asks to review, clean up, audit,
organize, or improve the quality of their task list.

## Procedure

1. Retrieve the user's current tasks using the available task tools.
2. Inspect the returned task data without modifying it.
3. Look for duplicate or very similar task titles.
4. Look for titles that appear malformed, unclear, or contain status
   information that belongs in the status field.
5. Look for task statuses that may deserve user review.
6. Produce a concise cleanup report.
7. Suggest possible corrections, but do not apply them automatically.

## Grounding Rules

- Treat the task data returned by the task system as the source of truth.
- Do not claim that a task is incorrect unless the data supports that conclusion.
- Clearly distinguish detected data issues from suggestions.
- Do not invent missing task information.
- Do not assume a task should be marked done merely because its title
  sounds related to completed work.

## Safety Rules

- Do not create tasks unless the user explicitly asks.
- Do not update tasks unless the user explicitly asks.
- Do not delete tasks unless the user explicitly asks.
- Never claim that a change was made unless the corresponding tool
  successfully completed the change.

## Output

Provide a concise task cleanup report in the user's language.
Keep task titles exactly as returned by the task system.
Separate detected issues from suggested actions.