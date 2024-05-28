from typing import List

from fastapi import Body, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from database.connection import get_db
from database.repository import get_todos, get_todo_by_todo_id, create_todo, update_todo, delete_todo
from database.orm import ToDo

from schema.response import ToDoListSchema, ToDoSchema
from schema.request import CreateToDoRequest


router = APIRouter(prefix="/todos")


@router.get("", status_code=200)
def get_todos_handler(
    order: str | None = None,
    session: Session = Depends(get_db),
) -> ToDoListSchema:
    todos: List[ToDo] = get_todos(session=session)
    
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
    session: Session = Depends(get_db),
) -> ToDoSchema:
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)
    if todo:
        return ToDoSchema.from_orm(todo)
    raise HTTPException(status_code=404, detail="ToDo Not Found")



@router.post("", status_code=201)
def create_todo_handler(
    request: CreateToDoRequest,
    session: Session = Depends(get_db),
) -> ToDoSchema:
    todo: ToDo = ToDo.create(request=request) # id=None
    todo: ToDo = create_todo(session=session, todo=todo) # id=int
    return ToDoSchema.from_orm(todo)


@router.patch("/{todo_id}", status_code=200)
def update_todo_handler(
    todo_id: int,
    is_done: bool = Body(..., embed=True),
    session: Session = Depends(get_db),
) -> ToDoSchema:
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)
    if todo:
        # if is_done is True:
        #     todo.done()
        # else:
        #     todo.undone()
        todo.done() if is_done else todo.undone()
        todo: ToDo = update_todo(session=session, todo=todo)
        return ToDoSchema.from_orm(todo)
    raise HTTPException(status_code=404, detail="ToDo Not Found")


@router.delete("/{todo_id}", status_code=204)
def delete_todo_handler(
    todo_id: int,
    session: Session = Depends(get_db),
):
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="ToDo Not Found")
    delete_todo(session=session, todo_id=todo_id)