import json

from backend.app.agents.client import client
from backend.app.agents.subagents import run_subagent


MODEL = "openai/gpt-oss-20b"


SYSTEM_PROMPT = (
    "You are the main orchestrator AI agent. "
    "Understand the user's language and respond naturally in the same language "
    "unless the user asks for another language. "
    "You can communicate in multiple languages. "
    "\n\n"
    "Your job is to route the user's request to the correct specialized agent. "
    "\n\n"
    "Use task_agent for ANY request that depends on the user's task data, "
    "including creating, viewing, updating, deleting, planning, prioritizing, "
    "reviewing, auditing, organizing, cleaning up, detecting duplicates, "
    "or identifying problems in the user's task list. "
    "\n\n"
    "Use research_agent for factual, technical, explanatory, or current-information "
    "questions that require external research and are not about the user's task data. "
    "\n\n"
    "Important routing examples: "
    "'Show me my tasks' -> task_agent. "
    "'What should I work on next?' -> task_agent. "
    "'Audit my tasks for duplicates' -> task_agent. "
    "'Create a task called Learn Kubernetes' -> task_agent. "
    "'What is PostgreSQL?' -> research_agent. "
    "'What is the latest MCP specification?' -> research_agent. "
    "\n\n"
    "Delegate the request to the most appropriate subagent. "
    "Do not perform task operations yourself."
)


SUBAGENT_TOOL = {
    "type": "function",
    "function": {
        "name": "delegate_to_subagent",
        "description": (
            "Delegate the user's request to the most appropriate "
            "specialized subagent."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "agent_name": {
                    "type": "string",
                    "enum": [
                        "task_agent",
                        "research_agent",
                    ],
                    "description": (
                        "The specialized subagent that should "
                        "handle the request."
                    ),
                },
                "user_message": {
                    "type": "string",
                    "description": (
                        "The user's original request to send "
                        "to the subagent."
                    ),
                },
            },
            "required": [
                "agent_name",
                "user_message",
            ],
        },
    },
}


def run_main_agent(
    conversation_id: str,
    user_message: str,
):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=[SUBAGENT_TOOL],
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message

    if not assistant_message.tool_calls:
        return {
            "response": assistant_message.content,
            "delegated_to": None,
        }

    tool_call = assistant_message.tool_calls[0]

    arguments = json.loads(
        tool_call.function.arguments or "{}"
    )

    agent_name = arguments["agent_name"]
    delegated_message = arguments["user_message"]

    result = run_subagent(
        agent_name=agent_name,
        conversation_id=conversation_id,
        user_message=delegated_message,
    )

    return {
        "response": result.get("response"),
        "delegated_to": agent_name,
        "subagent_result": result,
    }