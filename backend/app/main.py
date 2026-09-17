from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.db.database import engine, Base
from backend.app.models.task import Task
from backend.app.routers.task import router as tasks_router
from backend.app.routers.ai import router as ai_router


app = FastAPI(
    title="AI Task & Research Workspace API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)


app.include_router(tasks_router)
app.include_router(ai_router)


@app.get("/")
def home():
    return {
        "message": "AI Task & Research Workspace API"
    }