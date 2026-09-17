from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.models.task import Task
from backend.app.schemas.task import TaskCreate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(
        title=task.title,
        status=task.status
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    existing_task = db.query(Task).filter(Task.id == task_id).first()

    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    existing_task.title = task.title
    existing_task.status = task.status

    db.commit()
    db.refresh(existing_task)

    return existing_task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    existing_task = db.query(Task).filter(Task.id == task_id).first()

    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(existing_task)
    db.commit()

    return {"message": "Task deleted successfully"}