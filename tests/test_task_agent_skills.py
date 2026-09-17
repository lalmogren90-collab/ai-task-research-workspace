import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from backend.app.memory.store import clear_history, get_history


class TaskAgentSkillTests(unittest.TestCase):
    def test_skill_changes_each_turn_without_changing_history(self):
        prompts = []
        tool_call = SimpleNamespace(
            id="call-1",
            function=SimpleNamespace(name="get_tasks", arguments="{}"),
        )
        replies = iter([
            SimpleNamespace(role="assistant", content=None, tool_calls=[tool_call]),
            SimpleNamespace(role="assistant", content="Plan", tool_calls=[]),
            SimpleNamespace(role="assistant", content="Cleanup", tool_calls=[]),
            SimpleNamespace(role="assistant", content="Created", tool_calls=[]),
        ])

        def create(**kwargs):
            prompts.append(list(kwargs["messages"]))
            return SimpleNamespace(
                choices=[SimpleNamespace(message=next(replies))]
            )

        client = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=create))
        )
        skill_by_request = {
            "What should I work on next?": "task_planning",
            "Audit my tasks for duplicates.": "task_cleanup",
            "Create a task called Smoke Test.": None,
        }
        select_skill = Mock(side_effect=skill_by_request.__getitem__)
        call_mcp_tool = Mock(return_value={"result": []})
        modules = {
            "backend.app.agents.client": SimpleNamespace(client=client),
            "backend.app.mcp.client_helper": SimpleNamespace(
                call_mcp_tool=call_mcp_tool
            ),
            "backend.app.skills.selector": SimpleNamespace(
                select_skill=select_skill
            ),
        }
        agent_path = (
            Path(__file__).resolve().parents[1]
            / "backend/app/agents/task_agent.py"
        )
        spec = importlib.util.spec_from_file_location(
            "task_agent_skills_under_test", agent_path
        )
        agent = importlib.util.module_from_spec(spec)
        conversation_id = "test-skill-transitions"
        clear_history(conversation_id)

        try:
            with patch.dict(sys.modules, modules):
                spec.loader.exec_module(agent)

            results = [
                agent.run_agent(conversation_id, request)
                for request in skill_by_request
            ]

            self.assertEqual(
                [result["selected_skill"] for result in results],
                ["task_planning", "task_cleanup", None],
            )
            self.assertEqual(select_skill.call_count, 3)
            call_mcp_tool.assert_called_once_with("get_tasks", {})

            system_prompts = [messages[0]["content"] for messages in prompts]
            self.assertEqual(system_prompts[0], system_prompts[1])
            self.assertIn("Task Planning Skill", system_prompts[0])
            self.assertIn("Task Cleanup Skill", system_prompts[2])
            self.assertNotIn("Task Planning Skill", system_prompts[2])
            self.assertEqual(system_prompts[3], agent.SYSTEM_PROMPT)

            roles = [
                message["role"] if isinstance(message, dict) else message.role
                for message in get_history(conversation_id)
            ]
            self.assertEqual(
                roles,
                ["user", "assistant", "tool", "assistant",
                 "user", "assistant", "user", "assistant"],
            )
            self.assertEqual(roles[:5], [
                message["role"] if isinstance(message, dict) else message.role
                for message in prompts[2][1:]
            ])
            self.assertEqual(roles[:6], [
                message["role"] if isinstance(message, dict) else message.role
                for message in prompts[3][1:-1]
            ])
        finally:
            clear_history(conversation_id)


if __name__ == "__main__":
    unittest.main()
