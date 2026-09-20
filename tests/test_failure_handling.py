import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException


ROOT = Path(__file__).resolve().parents[1]


def load_with_dependencies(name, path, dependencies):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, dependencies):
        spec.loader.exec_module(module)
    return module


class SubagentFailureTests(unittest.TestCase):
    def setUp(self):
        self.agent = load_with_dependencies(
            "subagents_failure_test",
            "backend/app/agents/subagents.py",
            {
                "backend.app.agents.task_agent": SimpleNamespace(
                    run_agent=Mock()
                ),
                "backend.app.agents.client": SimpleNamespace(client=Mock()),
                "backend.app.tools.registry": SimpleNamespace(
                    execute_tool=Mock()
                ),
            },
        )

    def test_exception_returns_safe_error(self):
        secret = "internal credential detail"
        self.agent.SUBAGENTS["task_agent"] = Mock(
            side_effect=RuntimeError(secret)
        )

        result = self.agent.run_subagent("task_agent", "conversation", "hello")

        self.assertEqual(result, {"error": "Subagent execution failed."})
        self.assertNotIn(secret, str(result))

    def test_unknown_subagent_returns_error(self):
        self.assertEqual(
            self.agent.run_subagent("missing", "conversation", "hello"),
            {"error": "Unknown subagent."},
        )


class ChatFailureTests(unittest.TestCase):
    def setUp(self):
        self.run_main_agent = Mock()
        self.route = load_with_dependencies(
            "ai_failure_test",
            "backend/app/routers/ai.py",
            {
                "backend.app.agents.main_agent": SimpleNamespace(
                    run_main_agent=self.run_main_agent
                ),
            },
        )
        self.request = self.route.ChatRequest(
            conversation_id="conversation", message="hello"
        )

    def assert_safe_failure(self):
        with self.assertRaises(HTTPException) as raised:
            self.route.chat(self.request)
        self.assertEqual(raised.exception.status_code, 500)
        self.assertEqual(
            raised.exception.detail, "Unable to complete the request."
        )

    def test_subagent_error_is_not_empty_success(self):
        self.run_main_agent.return_value = {
            "response": None,
            "delegated_to": "task_agent",
            "subagent_result": {"error": "internal credential detail"},
        }
        self.assert_safe_failure()

    def test_unexpected_exception_is_safe(self):
        self.run_main_agent.side_effect = RuntimeError("internal credential detail")
        self.assert_safe_failure()

    def test_success_contract_is_preserved(self):
        self.run_main_agent.return_value = {
            "response": "Done",
            "delegated_to": "task_agent",
            "subagent_result": {"selected_skill": "task_planning"},
        }
        response = self.route.chat(self.request)
        self.assertEqual(response.response, "Done")
        self.assertEqual(response.delegated_to, "task_agent")
        self.assertEqual(response.selected_skill, "task_planning")


class TaskMonitorFailureTests(unittest.TestCase):
    def setUp(self):
        self.call_mcp_tool = Mock()
        self.run_main_agent = Mock()
        self.monitor = load_with_dependencies(
            "task_monitor_failure_test",
            "backend/app/automation/task_monitor.py",
            {
                "backend.app.agents.main_agent": SimpleNamespace(
                    run_main_agent=self.run_main_agent
                ),
                "backend.app.mcp.client_helper": SimpleNamespace(
                    call_mcp_tool=self.call_mcp_tool
                ),
            },
        )

    def test_mcp_error_is_not_empty_task_list(self):
        self.call_mcp_tool.return_value = {
            "error": "MCP tool execution failed.", "content": []
        }
        result = self.monitor.check_unfinished_tasks()
        self.assertEqual(
            result, {"triggered": False, "error": "Task retrieval failed."}
        )
        self.run_main_agent.assert_not_called()

    def test_mcp_exception_is_reported_safely(self):
        self.call_mcp_tool.side_effect = RuntimeError("internal credential detail")
        result = self.monitor.check_unfinished_tasks()
        self.assertEqual(
            result, {"triggered": False, "error": "Task retrieval failed."}
        )
        self.run_main_agent.assert_not_called()

    def test_empty_task_list_retains_existing_result(self):
        self.call_mcp_tool.return_value = {"result": []}
        self.assertEqual(
            self.monitor.check_unfinished_tasks(),
            {"triggered": False, "unfinished_tasks": []},
        )


if __name__ == "__main__":
    unittest.main()
