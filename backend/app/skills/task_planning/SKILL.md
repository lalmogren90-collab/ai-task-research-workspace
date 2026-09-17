# Task Planning Skill

## Purpose

Use this skill when the user asks for a plan, priorities, next steps,
or guidance about their current tasks.

## Procedure

1. Retrieve the user's current tasks using the available task tools.
2. Separate completed tasks from unfinished tasks.
3. Focus primarily on unfinished tasks.
4. Prioritize unfinished tasks using only information that is actually
   available in the task data and conversation.
5. If dependencies are explicitly present in the available data,
   use them when prioritizing.
6. If dependencies are not explicitly available, do not invent them.
7. Produce a concise and actionable plan.
8. Explain important priorities when they are supported by available evidence.

## Grounding Rules

- Treat task data returned by the task system as the source of truth.
- Do not invent task dependencies, deadlines, priorities, or statuses.
- Do not claim that one task is a prerequisite for another unless that
  relationship is explicitly supported by the available data or conversation.
- Clearly distinguish facts from suggestions.
- A suggested ordering is a recommendation, not a stored task dependency.

## Safety Rules

- Do not create tasks unless the user explicitly asks.
- Do not delete tasks unless the user explicitly asks.
- Do not update task status unless the user explicitly asks.
- Never claim that a task was changed unless the corresponding tool
  successfully completed the change.

## Output

Provide a clear prioritized action plan in the user's language.
Keep task titles exactly as returned by the task system.
When proposing an ordering without explicit dependency data, describe it
as a suggested order rather than a factual dependency.