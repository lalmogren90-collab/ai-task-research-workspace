import json

from backend.app.agents.client import client
from backend.app.agents.harness import AgentHarness
from backend.app.mcp.client_helper import call_mcp_tool
from backend.app.memory.store import get_history, add_message
from backend.app.memory.state import AgentState
from backend.app.skills.loader import load_skill
from backend.app.skills.selector import select_skill


MODEL = "openai/gpt-oss-20b"

MAX_STEPS = 5


SYSTEM_PROMPT = (
    "You are an intelligent AI assistant. "
    "Understand the user's language and respond naturally in the same language "
    "unless the user asks for another language. "
    "You can communicate in multiple languages. "
    "Be helpful, accurate, concise, and natural. "
    "You can use tools to manage the user's tasks. "
    "Use get_tasks whenever the user asks about their tasks, "
    "including requests such as listing tasks, showing tasks, "
    "asking what tasks they have, asking what they are working on, "
    "or asking for their current tasks. "
    "Use create_task whenever the user asks to create, add, "
    "make, or remember a new task. "
    "Use update_task whenever the user asks to change a task, "
    "including changing its title or status. "
    "Use delete_task whenever the user asks to delete or remove a task. "
    "Use the conversation history to understand references to previous messages."
)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task.",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["todo", "doing", "done"],
                        "description": "The task status.",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": "Get all tasks belonging to the user.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task. Use this to change the task title or status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update.",
                    },
                    "title": {
                        "type": "string",
                        "description": "The new title of the task.",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["todo", "doing", "done"],
                        "description": "The new task status.",
                    },
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete an existing task by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete.",
                    },
                },
                "required": ["task_id"],
            },
        },
    },
]


def build_agent_prompt(
    user_message: str,
) -> tuple[str, str | None]:

    selected_skill = select_skill(user_message)

    if selected_skill is None:
        return SYSTEM_PROMPT, None

    skill_content = load_skill(selected_skill)

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"You have selected the following skill: {selected_skill}\n\n"
        "Follow these skill instructions for the current request:\n\n"
        f"{skill_content}"
    )

    return prompt, selected_skill


def run_agent(conversation_id: str, user_message: str):

    harness = AgentHarness(conversation_id)
    selected_skill = None

    try:
        agent_prompt, selected_skill = build_agent_prompt(user_message)

        def current_messages():
            return [
                {"role": "system", "content": agent_prompt},
                *(
                    message
                    for message in get_history(conversation_id)
                    if (
                        message.get("role")
                        if isinstance(message, dict)
                        else message.role
                    ) != "system"
                ),
            ]

        add_message(
            conversation_id,
            {
                "role": "user",
                "content": user_message,
            },
        )

        state = AgentState(
            conversation_id=conversation_id,
            messages=current_messages(),
        )

        for step in range(MAX_STEPS):

            state.step_count = step + 1

            harness.start_step(state.step_count)

            response = client.chat.completions.create(
                model=MODEL,
                messages=state.messages,
                tools=TOOLS,
                tool_choice="auto",
            )

            assistant_message = response.choices[0].message

            add_message(
                conversation_id,
                assistant_message,
            )

            state.messages = current_messages()

            if not assistant_message.tool_calls:

                harness.finish()

                return {
                    "response": assistant_message.content,
                    "selected_skill": selected_skill,
                    "run": harness.get_run(),
                }

            for tool_call in assistant_message.tool_calls:

                tool_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments or "{}"
                )

                if tool_name == "get_tasks":
                    arguments = {}

                state.tool_calls.append(
                    {
                        "name": tool_name,
                        "arguments": arguments,
                    }
                )

                harness.record_tool_call(
                    tool_name,
                    arguments,
                )

                result = call_mcp_tool(
                    tool_name,
                    arguments,
                )

                state.tool_results.append(
                    {
                        "name": tool_name,
                        "result": result,
                    }
                )

                harness.record_tool_result(
                    tool_name,
                    result,
                )

                add_message(
                    conversation_id,
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(
                            result,
                            ensure_ascii=False,
                        ),
                    },
                )

                state.messages = current_messages()

        harness.finish()

        return {
            "response": "The agent reached its maximum number of steps.",
            "selected_skill": selected_skill,
            "run": harness.get_run(),
        }

    except Exception as error:

        harness.record_error(str(error))
        harness.finish()

        return {
            "response": "The agent encountered an error.",
            "selected_skill": selected_skill,
            "run": harness.get_run(),
        }
