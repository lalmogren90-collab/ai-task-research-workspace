from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from backend.app.mcp.client_helper import call_mcp_tool


PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "backend" / "generated"
CHART_PATH = OUTPUT_DIR / "task_status_chart.png"


def analyze_tasks() -> dict:
    """
    Retrieve task data through MCP, execute Python analytics,
    and generate a task-status chart.
    """
    result = call_mcp_tool("get_tasks", {})

    if isinstance(result, dict):
        tasks = result.get("result", [])
    else:
        tasks = result

    if not isinstance(tasks, list):
        raise RuntimeError(f"Unexpected MCP task result: {result}")

    status_counts = Counter(
        str(task.get("status", "unknown")).strip().lower()
        for task in tasks
    )

    total = len(tasks)
    done = status_counts.get("done", 0)
    todo = status_counts.get("todo", 0)
    completion_rate = round((done / total) * 100, 1) if total else 0.0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    labels = list(status_counts.keys())
    values = [status_counts[label] for label in labels]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values)

    ax.set_title("Task Status Analysis")
    ax.set_xlabel("Status")
    ax.set_ylabel("Number of Tasks")
    ax.set_ylim(0, max(values, default=1) + 2)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value,
            str(value),
            ha="center",
            va="bottom",
        )

    fig.tight_layout()
    fig.savefig(CHART_PATH, dpi=160)
    plt.close(fig)

    return {
        "total_tasks": total,
        "status_counts": dict(status_counts),
        "done_tasks": done,
        "open_tasks": todo,
        "completion_rate": completion_rate,
        "chart_path": str(CHART_PATH),
    }


if __name__ == "__main__":
    analysis = analyze_tasks()

    print("=== Agent Analytics Tool ===")
    print("Data source: MCP get_tasks")
    print("Execution: Python analytics + Matplotlib")
    print(f"Total tasks: {analysis['total_tasks']}")
    print(f"Status counts: {analysis['status_counts']}")
    print(f"Completion rate: {analysis['completion_rate']}%")
    print(f"Chart generated: {analysis['chart_path']}")
