from dataclasses import dataclass, field


@dataclass
class AgentState:
    conversation_id: str
    messages: list = field(default_factory=list)
    tool_calls: list = field(default_factory=list)
    tool_results: list = field(default_factory=list)
    step_count: int = 0