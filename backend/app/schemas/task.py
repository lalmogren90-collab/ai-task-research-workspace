from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    status: str = "todo"


class TaskResponse(BaseModel):
    id: int
    title: str
    status: str

    class Config:
        from_attributes = True