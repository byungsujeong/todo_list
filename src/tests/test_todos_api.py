# from fastapi.testclient import TestClient

from database.repository import ToDoRepository, UserRepository
from database.orm import ToDo, User

from service.user import UserService


def test_get_todos(client, mocker):
    access_token: str = UserService().create_jwt(username="user1")
    headers = {"Authorization": f"Bearer {access_token}"}
    user = User(id=1, username="user1", password="hashed")
    user.todos = [
        ToDo(id=1, contents="test1", is_done=True),
        ToDo(id=2, contents="test2", is_done=False),
    ]

    mocker.patch.object(UserRepository, "get_user_by_username", return_value=user)
    response = client.get("/todos", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["todos"]) == 2

def test_get_todos_order(client, mocker):
    access_token: str = UserService().create_jwt(username="user1")
    headers = {"Authorization": f"Bearer {access_token}"}
    user = User(id=1, username="user1", password="hashed")
    user.todos = [
        ToDo(id=1, contents="test1", is_done=True),
        ToDo(id=2, contents="test2", is_done=False),
    ]

    mocker.patch.object(UserRepository, "get_user_by_username", return_value=user)
    response = client.get("/todos", headers=headers)
    assert response.status_code == 200
    assert response.json()["todos"][0]["id"] == 1

    # order = DESC
    response = client.get("/todos?order=DESC", headers=headers)
    assert response.status_code == 200
    assert response.json()["todos"][0]["id"] != 1


def test_get_todo(client, mocker):
    # normal
    mocker.patch.object(ToDoRepository, "get_todo_by_todo_id", return_value=
                 ToDo(id=1, contents="test1", is_done=True)
    )
    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

    # 404
    mocker.patch.object(ToDoRepository, "get_todo_by_todo_id", return_value=None)
    response = client.get("/todos/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "ToDo Not Found"


def test_create_todo(client, mocker):
    create_spy = mocker.spy(ToDo, "create")
    mocker.patch.object(ToDoRepository, "create_todo", return_value=
                 ToDo(id=1, contents="test1", is_done=True)
    )
    body = {
        "contents": "test1",
        "is_done": False,
    }
    response = client.post("/todos", json=body)
    assert create_spy.spy_return.id is None
    assert create_spy.spy_return.contents == "test1"
    assert create_spy.spy_return.is_done is False
    assert response.status_code == 201
    assert response.json()["id"] == 1


def test_update_todo(client, mocker):
    # normal
    mocker.patch.object(ToDoRepository, "get_todo_by_todo_id", return_value=
                 ToDo(id=1, contents="test1", is_done=True)
    )
    undone = mocker.patch.object(ToDo, "undone")
    mocker.patch.object(ToDoRepository, "update_todo", return_value=
                 ToDo(id=1, contents="test1", is_done=False)
    )
    response = client.patch("/todos/1", json={"is_done": False})

    undone.assert_called_once_with()

    assert response.status_code == 200
    assert response.json()["id"] == 1

    # 404
    mocker.patch.object(ToDoRepository, "get_todo_by_todo_id", return_value=None)
    response = client.patch("/todos/99", json={"is_done": True})
    assert response.status_code == 404
    assert response.json()["detail"] == "ToDo Not Found"


def test_delete_todo(client, mocker):
    # 204
    mocker.patch.object(ToDoRepository, "get_todo_by_todo_id", return_value=
                 ToDo(id=1, contents="test1", is_done=True)
    )
    mocker.patch.object(ToDoRepository, "delete_todo", return_value=None)
    response = client.delete("/todos/1")
    assert response.status_code == 204

    # 404
    mocker.patch.object(ToDoRepository, "get_todo_by_todo_id", return_value=None)
    response = client.delete("/todos/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "ToDo Not Found"
