import json

from backend.app.agents.task_agent import run_agent
from backend.app.agents.client import client
from backend.app.tools.registry import execute_tool

MODEL = "openai/gpt-oss-20b"


RESEARCH_SYSTEM_PROMPT = (
    "You are a specialized research assistant. "
    "Understand the user's language and respond naturally in the same language "
    "unless the user asks for another language. "
    "Your job is to research factual, technical, and current information. "
    "Use the web_search tool to gather evidence before answering. "
    "Prefer authoritative and official sources."
)


FINAL_ANSWER_SYSTEM_PROMPT = (
    "You are a research answer writer. "
    "You do not have access to tools. "
    "Do not attempt to call or simulate any tool. "
    "Answer the user's question using only the provided web search results. "
    "Treat the search results as the source of truth. "
    "Do not add unsupported facts from memory. "
    "If the evidence is insufficient or conflicting, say so clearly. "
    "Prefer official and authoritative sources. "
    "Include relevant source URLs from the provided results. "
    "Respond naturally in the same language as the user's question "
    "unless the user requests another language."
)


RESEARCH_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the live web for factual, technical, or current "
                "information. Returns titles, URLs, content, and relevance scores."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The exact web search query.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of search results to return.",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    }
]


def task_agent(conversation_id: str, user_message: str):
    return run_agent(
        conversation_id=conversation_id,
        user_message=user_message,
    )


def research_agent(conversation_id: str, user_message: str):
    research_messages = [
        {
            "role": "system",
            "content": RESEARCH_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]

    # Step 1:
    # Force the research model to use web_search.
    research_response = client.chat.completions.create(
        model=MODEL,
        messages=research_messages,
        tools=RESEARCH_TOOLS,
        tool_choice="required",
    )

    assistant_message = research_response.choices[0].message

    if not assistant_message.tool_calls:
        return {
            "response": "The research agent did not produce a web search request.",
            "agent": "research_agent",
        }

    all_results = []

    # Step 2:
    # Execute requested web searches.
    for tool_call in assistant_message.tool_calls:
        tool_name = tool_call.function.name

        try:
            arguments = json.loads(
                tool_call.function.arguments or "{}"
            )
        except json.JSONDecodeError:
            arguments = {}

        result = execute_tool(
            tool_name,
            arguments,
        )

        all_results.append(
            {
                "tool": tool_name,
                "arguments": arguments,
                "result": result,
            }
        )

    # Step 3:
    # Create a completely fresh conversation for the final answer.
    # We intentionally do NOT include the earlier tool-call messages here.
    evidence = json.dumps(
        all_results,
        ensure_ascii=False,
        indent=2,
    )

    final_messages = [
        {
            "role": "system",
            "content": FINAL_ANSWER_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": (
                f"Original question:\n"
                f"{user_message}\n\n"
                f"Web search results:\n"
                f"{evidence}\n\n"
                f"Now answer the original question using only "
                f"the web search results above."
            ),
        },
    ]

    final_response = client.chat.completions.create(
        model=MODEL,
        messages=final_messages,
    )

    final_message = final_response.choices[0].message

    return {
        "response": final_message.content,
        "agent": "research_agent",
    }


SUBAGENTS = {
    "task_agent": task_agent,
    "research_agent": research_agent,
}


def run_subagent(
    agent_name: str,
    conversation_id: str,
    user_message: str,
):
    agent = SUBAGENTS.get(agent_name)

    if not agent:
        return {
            "error": "Unknown subagent."
        }

    try:
        return agent(
            conversation_id,
            user_message,
        )

    except Exception:
        return {
            "error": "Subagent execution failed."
        }
