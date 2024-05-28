import bcrypt

from fastapi import Depends

from database.repository import UserRepository
from database.orm import User

from service.user import UserService


def test_user_sign_up(client, mocker,):
    hash_password = mocker.patch.object(
        UserService,
        "hash_password",
        return_value="hashed"
    )
    user_create = mocker.patch.object(
        User,
        "create",
        return_value=User(id=None, username="user1", password="hashed")
    )
    mocker.patch.object(
        UserRepository,
        "save_user",
        return_value=User(id=1, username="user1", password="hashed")
    )

    body = {
        "username": "user1",
        "password": "1q2w3e4r!@",
    }

    response = client.post("/users/sign-up", json=body)
    
    hash_password.assert_called_once_with(
        plain_password="1q2w3e4r!@"
    )
    user_create.assert_called_once_with(
        username="user1",
        hashed_password="hashed",
    )
    assert response.status_code == 201
    assert response.json() == {"id":1, "username": "user1"}  
    