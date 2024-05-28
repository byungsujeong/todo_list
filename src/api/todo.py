from typing import List

from fastapi import Body, HTTPException, Depends, APIRouter

from security import get_access_token

from database.connection import get_db
from database.repository import ToDoRepository, UserRepository
from database.orm import ToDo, User

from schema.response import ToDoListSchema, ToDoSchema
from schema.request import CreateToDoRequest

from service.user import UserService


router = APIRouter(prefix="/todos")


@router.get("", status_code=200)
def get_todos_handler(
    access_token: str = Depends(get_access_token),
    order: str | None = None,
    user_service: UserService = Depends(),
    user_repo: UserRepository = Depends(),
    todo_repo: ToDoRepository = Depends(ToDoRepository),
    # todo_repo: ToDoRepository = Depends(생략가능),
) -> ToDoListSchema:
    
    username: str = user_service.decode_jwt(access_token=access_token)

    user: User | None = user_repo.get_user_by_username(username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")
    
    todos: List[ToDo] = user.todos
    # todos: List[ToDo] = todo_repo.get_todos()
    if order == "DESC":
        return ToDoListSchema(
            todos=[ToDoSchema.from_orm(todo) for todo in todos[::-1]]
        )
    return ToDoListSchema(
        todos=[ToDoSchema.from_orm(todo) for todo in todos]
    )


@router.get("/{todo_id}", status_code=200)
def get_todo_handler(
    todo_id: int,
    todo_repo: ToDoRepository = Depends(ToDoRepository),
) -> ToDoSchema:
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    if todo:
        return ToDoSchema.from_orm(todo)
    raise HTTPException(status_code=404, detail="ToDo Not Found")



@router.post("", status_code=201)
def create_todo_handler(
    request: CreateToDoRequest,
    todo_repo: ToDoRepository = Depends(ToDoRepository),
) -> ToDoSchema:
    todo: ToDo = ToDo.create(request=request) # id=None
    todo: ToDo = todo_repo.create_todo(todo=todo) # id=int
    return ToDoSchema.from_orm(todo)


@router.patch("/{todo_id}", status_code=200)
def update_todo_handler(
    todo_id: int,
    is_done: bool = Body(..., embed=True),
    todo_repo: ToDoRepository = Depends(ToDoRepository),
) -> ToDoSchema:
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    if todo:
        # if is_done is True:
        #     todo.done()
        # else:
        #     todo.undone()
        todo.done() if is_done else todo.undone()
        todo: ToDo = todo_repo.update_todo(todo=todo)
        return ToDoSchema.from_orm(todo)
    raise HTTPException(status_code=404, detail="ToDo Not Found")


@router.delete("/{todo_id}", status_code=204)
def delete_todo_handler(
    todo_id: int,
    todo_repo: ToDoRepository = Depends(ToDoRepository),
):
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="ToDo Not Found")
    todo_repo.delete_todo(todo_id=todo_id)
