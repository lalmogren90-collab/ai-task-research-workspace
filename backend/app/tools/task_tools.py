from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.models.task import Task


def create_task(title: str, status: str = "todo"):
    db: Session = SessionLocal()

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


def get_tasks():
    db: Session = SessionLocal()

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


def update_task(
    task_id: int,
    title: str | None = None,
    status: str | None = None,
):
    db: Session = SessionLocal()

    try:
        task = db.query(Task).filter(Task.id == task_id).first()

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


def delete_task(task_id: int):
    db: Session = SessionLocal()

    try:
        task = db.query(Task).filter(Task.id == task_id).first()

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

def research_topic(topic: str):
    return {
        "topic": topic,
        "information": (
            "MCP stands for Model Context Protocol. "
            "It is an open protocol that standardizes how AI applications "
            "connect to external tools, data sources, and systems. "
            "It allows an AI application to discover and use capabilities "
            "provided by external MCP servers."
        ),
        "source": "Internal research knowledge base",
    }
import os

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()


def web_search(query: str, max_results: int = 5):
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return {
            "error": "TAVILY_API_KEY is not set."
        }

    client = TavilyClient(api_key=api_key)

    try:
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
        )

        results = []

        for item in response.get("results", []):
            results.append(
                {
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "content": item.get("content"),
                    "score": item.get("score"),
                }
            )

        return {
            "query": query,
            "results": results,
        }

    except Exception as error:
        return {
            "error": f"Web search failed: {str(error)}"
        }