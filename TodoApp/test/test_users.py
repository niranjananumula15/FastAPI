from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    res = client.get("/users")
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['username'] == "sunny"


def test_change_password(test_user):
    res = client.put(
        "/users/password",
        json={
            "password": "testpassword",
            "new_password": "newpassword"
        }
    )

    assert res.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_fail(test_user):
    res = client.put(
        "/users/password",
        json={
            "password": "wrongpassword",
            "new_password": "newpassword"
        }
    )

    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert res.json()['detail'] == "Password is incorrect"


