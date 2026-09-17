import sys
from pathlib import Path

from mcp.server import MCPServer


PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.app.db.database import SessionLocal
from backend.app.models.task import Task


mcp = MCPServer("AI Training MCP Server")


@mcp.tool()
def get_tasks() -> list[dict]:
    """Get all tasks from the PostgreSQL database."""
    db = SessionLocal()

    try:
        tasks = db.query(Task).order_by(Task.id).all()

        return [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status,
            }
            for task in tasks
        ]

    finally:
        db.close()


@mcp.tool()
def create_task(
    title: str,
    status: str = "todo",
) -> dict:
    """Create a new task in the PostgreSQL database."""
    db = SessionLocal()

    try:
        new_task = Task(
            title=title,
            status=status,
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return {
            "id": new_task.id,
            "title": new_task.title,
            "status": new_task.status,
        }

    finally:
        db.close()


@mcp.tool()
def update_task(
    task_id: int,
    title: str | None = None,
    status: str | None = None,
) -> dict:
    """Update an existing task in the PostgreSQL database."""
    db = SessionLocal()

    try:
        task = db.query(Task).filter(
            Task.id == task_id
        ).first()

        if not task:
            return {
                "error": f"Task with id {task_id} not found."
            }

        if title is not None:
            task.title = title

        if status is not None:
            task.status = status

        db.commit()
        db.refresh(task)

        return {
            "id": task.id,
            "title": task.title,
            "status": task.status,
        }

    finally:
        db.close()


@mcp.tool()
def delete_task(
    task_id: int,
) -> dict:
    """Delete an existing task from the PostgreSQL database."""
    db = SessionLocal()

    try:
        task = db.query(Task).filter(
            Task.id == task_id
        ).first()

        if not task:
            return {
                "error": f"Task with id {task_id} not found."
            }

        deleted_task = {
            "id": task.id,
            "title": task.title,
            "status": task.status,
        }

        db.delete(task)
        db.commit()

        return {
            "message": "Task deleted successfully.",
            "task": deleted_task,
        }

    finally:
        db.close()