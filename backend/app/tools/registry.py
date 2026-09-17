from backend.app.tools.task_tools import (
    create_task,
    get_tasks,
    update_task,
    delete_task,
    research_topic,
    web_search,
)


TOOL_REGISTRY = {
    "create_task": create_task,
    "get_tasks": get_tasks,
    "update_task": update_task,
    "delete_task": delete_task,
    "research_topic": research_topic,
    "web_search": web_search,
}


def execute_tool(tool_name: str, arguments: dict):
    tool = TOOL_REGISTRY.get(tool_name)

    if not tool:
        return {
            "error": f"Unknown tool: {tool_name}"
        }

    try:
        return tool(**arguments)

    except Exception as error:
        return {
            "error": f"Tool execution failed: {str(error)}"
        }