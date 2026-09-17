from backend.app.agents.main_agent import run_main_agent
from backend.app.mcp.client_helper import call_mcp_tool
from backend.app.skills.loader import list_skills
from backend.app.skills.selector import select_skill


def check(name: str, condition: bool):
    if condition:
        print(f"PASS: {name}")
        return

    raise AssertionError(
        f"FAIL: {name}"
    )


print("\n=== FINAL AGENTIC APPLICATION SMOKE TEST ===\n")


# 1. Skills discovery

skills = list_skills()

check(
    "task_planning skill discovered",
    "task_planning" in skills,
)

check(
    "task_cleanup skill discovered",
    "task_cleanup" in skills,
)


# 2. Dynamic skill selection

check(
    "planning request selects task_planning",
    select_skill(
        "What should I work on next?"
    ) == "task_planning",
)

check(
    "cleanup request selects task_cleanup",
    select_skill(
        "Audit my tasks for duplicates."
    ) == "task_cleanup",
)

check(
    "CRUD request selects no skill",
    select_skill(
        "Create a task called Smoke Test."
    ) is None,
)


# 3. MCP connectivity

task_result = call_mcp_tool(
    "get_tasks",
    {},
)

check(
    "MCP get_tasks returned task data",
    isinstance(
        task_result.get("result"),
        list,
    ),
)


# 4. Main Agent -> Task Agent -> Skill -> MCP

planning_result = run_main_agent(
    conversation_id="final-smoke-planning",
    user_message=(
        "Review my unfinished tasks and tell me "
        "what I should work on next. "
        "Do not modify anything."
    ),
)

check(
    "planning delegated to task_agent",
    planning_result.get(
        "delegated_to"
    ) == "task_agent",
)

check(
    "task_planning skill used",
    planning_result.get(
        "subagent_result",
        {},
    ).get(
        "selected_skill"
    ) == "task_planning",
)


# 5. Main Agent -> Research Agent

research_result = run_main_agent(
    conversation_id="final-smoke-research",
    user_message=(
        "What is PostgreSQL? "
        "Give me a short explanation."
    ),
)

check(
    "research delegated to research_agent",
    research_result.get(
        "delegated_to"
    ) == "research_agent",
)

check(
    "research produced a response",
    bool(
        research_result.get("response")
    ),
)


print(
    "\nALL FINAL SMOKE TESTS PASSED"
)