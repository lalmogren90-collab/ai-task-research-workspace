from pydantic import BaseModel
from fastapi import APIRouter

from backend.app.agents.main_agent import run_main_agent


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


class ChatRequest(BaseModel):
    conversation_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    delegated_to: str | None = None
    selected_skill: str | None = None


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):
    result = run_main_agent(
        conversation_id=request.conversation_id,
        user_message=request.message,
    )

    subagent_result = result.get(
        "subagent_result",
        {},
    )

    return ChatResponse(
        response=result.get("response") or "",
        delegated_to=result.get("delegated_to"),
        selected_skill=subagent_result.get(
            "selected_skill"
        ),
    )