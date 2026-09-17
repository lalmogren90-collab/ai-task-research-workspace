from datetime import datetime, timezone

from backend.app.agents.main_agent import run_main_agent


def run_daily_task_summary():
    conversation_id = (
        f"automation-daily-tasks-"
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    )

    user_message = (
        "Show me my current tasks. "
        "Focus on unfinished tasks and give me a short daily summary "
        "of what I should work on."
    )

    print("Starting daily task automation...")

    result = run_main_agent(
        conversation_id=conversation_id,
        user_message=user_message,
    )

    print("\nDaily Task Summary:")
    print(result["response"])

    print("\nDelegated to:")
    print(result["delegated_to"])

    return result


if __name__ == "__main__":
    run_daily_task_summary()