from datetime import datetime, timezone

from backend.app.agents.main_agent import run_main_agent
from backend.app.mcp.client_helper import call_mcp_tool


def check_unfinished_tasks():
    print("Checking for unfinished tasks...")

    try:
        result = call_mcp_tool(
            "get_tasks",
            {},
        )
    except Exception:
        result = None

    if (
        not isinstance(result, dict)
        or "error" in result
        or not isinstance(result.get("result"), list)
    ):
        print("Task retrieval failed.")
        return {
            "triggered": False,
            "error": "Task retrieval failed.",
        }

    tasks = result["result"]

    unfinished_tasks = [
        task
        for task in tasks
        if task.get("status") != "done"
    ]

    if not unfinished_tasks:
        print("No unfinished tasks found.")
        print("No agent action is needed.")

        return {
            "triggered": False,
            "unfinished_tasks": [],
        }

    print(
        f"Condition matched: "
        f"{len(unfinished_tasks)} unfinished task(s) found."
    )

    conversation_id = (
        f"automation-task-monitor-"
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%S')}"
    )

    user_message = (
        "Review my current unfinished tasks. "
        "Give me a short prioritized action plan. "
        "Do not create, update, or delete any tasks."
    )

    print("Triggering the agent...")

    agent_result = run_main_agent(
        conversation_id=conversation_id,
        user_message=user_message,
    )

    print("\nAgent Action Plan:")
    print(agent_result["response"])

    return {
        "triggered": True,
        "unfinished_tasks": unfinished_tasks,
        "agent_result": agent_result,
    }


if __name__ == "__main__":
    check_unfinished_tasks()
