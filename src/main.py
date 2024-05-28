from fastapi import FastAPI
from dotenv import load_dotenv
from os import path, environ

from api import todo, user


base_dir = path.dirname(path.dirname(path.abspath(__file__)))
load_dotenv(path.join(base_dir, ".env"))

app = FastAPI()
app.include_router(todo.router)
app.include_router(user.router)


@app.get("/")
def health_check_handler():
    return {"ping": "pong"}



