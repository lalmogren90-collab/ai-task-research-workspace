import json

from backend.app.agents.client import client
from backend.app.skills.loader import list_skills


MODEL = "openai/gpt-oss-20b"


def select_skill(user_message: str) -> str | None:
    available_skills = list_skills()

    if not available_skills:
        return None

    system_prompt = (
        "You are a strict skill selector for a task-management agent. "
        "Select exactly one relevant skill, or select none. "
        "Do not select a skill merely because the request mentions tasks. "
        "\n\n"
        "Selection rules:\n"
        "- Select task_planning ONLY when the user asks for planning, "
        "prioritization, next steps, what to work on next, or guidance "
        "about how to approach their tasks.\n"
        "- Select task_cleanup ONLY when the user asks to audit, review, "
        "clean up, organize, detect duplicates, detect malformed titles, "
        "or identify data-quality problems in their task list.\n"
        "- Select none for ordinary CRUD operations such as creating, "
        "listing, updating, completing, renaming, or deleting tasks.\n"
        "- Select none when no available skill clearly matches the request.\n"
        "\n"
        "Examples:\n"
        "User: Create a task called Learn Kubernetes.\n"
        "Selection: none\n"
        "User: Show me my tasks.\n"
        "Selection: none\n"
        "User: Mark task 4 as done.\n"
        "Selection: none\n"
        "User: What should I work on next?\n"
        "Selection: task_planning\n"
        "User: Review my tasks for duplicates and malformed titles.\n"
        "Selection: task_cleanup\n"
    )

    selection_tool = {
        "type": "function",
        "function": {
            "name": "select_skill",
            "description": (
                "Select one skill only when it clearly matches "
                "the user's request."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "enum": available_skills + ["none"],
                    }
                },
                "required": ["skill_name"],
            },
        },
    }

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        tools=[selection_tool],
        tool_choice="required",
    )

    message = response.choices[0].message

    if not message.tool_calls:
        return None

    arguments = json.loads(
        message.tool_calls[0].function.arguments or "{}"
    )

    skill_name = arguments.get("skill_name")

    if skill_name == "none":
        return None

    if skill_name not in available_skills:
        return None

    return skill_name