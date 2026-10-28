
from datetime import timedelta, datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext

from ..database import SessionLocal
from ..models import users


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "60f8f5cf73c4e9cbcc4be9235b1f758acbbbe9d6d041e704b1b5231b789e744d"
ALGORITHM = "HS256"

bcrypt_user = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def create_access_token(
    username: str,
    user_id: int,
    role: str,
    expires_delta: timedelta
):
    encode = {
        "sub": username,
        "id": user_id,
        "role": role
    }

    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: Annotated[str, Depends(oauth_bearer)]
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        user_id = payload.get("id")
        user_role = payload.get("role")

        if username is None or user_id is None or user_role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        return {
            "username": username,
            "id": user_id,
            "user_role": user_role
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


class Createuserrequest(BaseModel):
    username: str
    email: str
    firstname: str
    lastname: str
    password: str
    role: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


@router.get("/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={}
    )


def authenticate_user(
    username: str,
    password: str,
    db: Session
):
    user = db.query(users).filter(
        users.username == username
    ).first()

    if not user:
        return False

    if not user.is_active:
        return False

    if not bcrypt_user.verify(password, user.hashed_password):
        return False

    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    create_userrequest: Createuserrequest,
    db: Session = Depends(get_db)
):
    existing_username = db.query(users).filter(
        users.username == create_userrequest.username
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    existing_email = db.query(users).filter(
        users.email == create_userrequest.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    new_user = users(
        email=create_userrequest.email,
        username=create_userrequest.username,
        first_name=create_userrequest.firstname,
        last_name=create_userrequest.lastname,
        role="user",
        hashed_password=bcrypt_user.hash(create_userrequest.password),
        is_active=True
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User registered successfully",
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }

    except Exception:
        db.rollback()
        raise


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = authenticate_user(
        form_data.username,
        form_data.password,
        db
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token(
        user.username,
        user.id,
        user.role,
        timedelta(minutes=20)
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
