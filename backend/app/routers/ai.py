import base64

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from backend.app.agents.client import client
from backend.app.agents.main_agent import run_main_agent


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


VISION_MODEL = "qwen/qwen3.8-27b"

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_IMAGE_SIZE = 10 * 1024 * 1024


class ChatRequest(BaseModel):
    conversation_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    delegated_to: str | None = None
    selected_skill: str | None = None


class VisionResponse(BaseModel):
    response: str
    model: str
    content_type: str


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):
    try:
        result = run_main_agent(
            conversation_id=request.conversation_id,
            user_message=request.message,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to complete the request.",
        ) from exc

    subagent_result = result.get(
        "subagent_result",
        {},
    )

    if subagent_result.get("error") or not result.get("response"):
        raise HTTPException(
            status_code=500,
            detail="Unable to complete the request.",
        )

    return ChatResponse(
        response=result["response"],
        delegated_to=result.get("delegated_to"),
        selected_skill=subagent_result.get(
            "selected_skill"
        ),
    )


@router.post(
    "/vision",
    response_model=VisionResponse,
)
async def vision(
    prompt: str = Form(...),
    image: UploadFile = File(...),
):
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, and WebP images are supported.",
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image is empty.",
        )

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image is too large.",
        )

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    image_url = (
        f"data:{image.content_type};base64,{encoded_image}"
    )

    try:
        completion = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the multimodal vision component of an "
                        "AI workspace. Analyze the supplied image together "
                        "with the user's text request. Base your answer only "
                        "on information visible in the image and the user's "
                        "request. If something cannot be determined from the "
                        "image, say so clearly."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                            },
                        },
                    ],
                },
            ],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to analyze the image.",
        ) from exc

    response_text = completion.choices[0].message.content

    if not response_text:
        raise HTTPException(
            status_code=500,
            detail="The vision model returned an empty response.",
        )

    return VisionResponse(
        response=response_text,
        model=VISION_MODEL,
        content_type=image.content_type,
    )