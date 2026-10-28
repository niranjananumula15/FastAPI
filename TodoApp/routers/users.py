
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext

from ..database import SessionLocal
from ..models import users
from .auth import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

bcrypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)


@router.get("/user", status_code=status.HTTP_200_OK)
async def get_user(
    user: user_dependency,
    db: db_dependency
):
    user_model = db.query(users).filter(
        users.id == user["id"]
    ).first()

    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "id": user_model.id,
        "email": user_model.email,
        "username": user_model.username,
        "first_name": user_model.first_name,
        "last_name": user_model.last_name,
        "is_active": user_model.is_active,
        "role": user_model.role
    }


@router.put("/user/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency,
    db: db_dependency,
    password_request: ChangePasswordRequest
):
    user_model = db.query(users).filter(
        users.id == user["id"]
    ).first()

    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not bcrypt_context.verify(
        password_request.current_password,
        user_model.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    try:
        user_model.hashed_password = bcrypt_context.hash(
            password_request.new_password
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
