
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status

from ..database import SessionLocal
from ..models import Todos
from .auth import get_current_user


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return db.query(Todos).all()


@router.delete(
    "/todo/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_todo(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(gt=0)
):
    if user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    todo_model = db.query(Todos).filter(
        Todos.id == todo_id
    ).first()

    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    db.delete(todo_model)
    db.commit()
