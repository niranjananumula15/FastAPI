from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import pytest
from ..models import Todos, users as User
from ..routers.auth import bcrypt_user

SQLALCHEMY_DATABASE_URI = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {
        "username": "sunny",
        "id": 1,
        "user_role": "admin",
    }


client = TestClient(app)


@pytest.fixture
def test_todo():
    db = TestingSessionLocal()

    todo = Todos(
        title="learn to code",
        description="learn to code",
        priority=5,
        complete=False,
        owner_id=1,
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)

    yield todo

    db.query(Todos).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_user():
    db = TestingSessionLocal()

    user = User(
        username="sunny",
        email="sunny@gmail.com",
        first_name="sunny",
        last_name="sunny",
        hashed_password=bcrypt_user.hash("testpassword"),
        role="admin",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    yield user

    db.query(User).filter(User.id == user.id).delete()
    db.commit()
    db.close()
