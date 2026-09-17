from datetime import datetime, timezone
from uuid import uuid4


class AgentHarness:

    def __init__(self, conversation_id: str):
        self.run_id = str(uuid4())
        self.conversation_id = conversation_id
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.steps = []
        self.errors = []
        self.finished_at = None

    def start_step(self, step_number: int):
        step = {
            "step": step_number,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "tool_calls": [],
            "tool_results": [],
        }

        self.steps.append(step)

        return step

    def record_tool_call(self, name: str, arguments: dict):
        self.steps[-1]["tool_calls"].append(
            {
                "name": name,
                "arguments": arguments,
            }
        )

    def record_tool_result(self, name: str, result):
        self.steps[-1]["tool_results"].append(
            {
                "name": name,
                "result": result,
            }
        )

    def record_error(self, error: str):
        self.errors.append(
            {
                "error": error,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def finish(self):
        self.finished_at = datetime.now(timezone.utc).isoformat()

    def get_run(self):
        return {
            "run_id": self.run_id,
            "conversation_id": self.conversation_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "steps": self.steps,
            "errors": self.errors,
        }