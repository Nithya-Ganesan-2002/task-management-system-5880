"""API endpoints for task CRUD."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from . import schemas, models, database, auth

from typing import List, Optional

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

# PUBLIC_INTERFACE
@router.get("/", summary="Get user tasks, filterable", response_model=List[schemas.TaskRead])
def read_tasks(
    q: Optional[str] = Query(None, description="Search string (in title or description)"),
    completed: Optional[bool] = Query(None, description="Filter by completion"),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """List all tasks for user. Supports filtering/searching."""
    query = db.query(models.Task).filter(models.Task.owner_id == current_user.id)
    if completed is not None:
        query = query.filter(models.Task.is_completed == completed)
    if q:
        query = query.filter(
            (models.Task.title.ilike(f"%{q}%")) |
            (models.Task.description.ilike(f"%{q}%"))
        )
    return query.order_by(models.Task.created_at.desc()).all()

# PUBLIC_INTERFACE
@router.post("/", summary="Create a new task", response_model=schemas.TaskRead, status_code=201)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Create a new task owned by the authenticated user."""
    t = models.Task(**task.dict(), owner_id=current_user.id)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

# PUBLIC_INTERFACE
@router.put("/{task_id}", summary="Update a task", response_model=schemas.TaskRead)
def update_task(
    task_id: int,
    task_data: schemas.TaskUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Update a user's task."""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for var, value in task_data.dict(exclude_unset=True).items():
        setattr(task, var, value)
    db.commit()
    db.refresh(task)
    return task

# PUBLIC_INTERFACE
@router.delete("/{task_id}", summary="Delete a task", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Delete a user's task."""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None
