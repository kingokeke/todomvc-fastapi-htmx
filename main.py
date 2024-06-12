import time
from typing import Annotated
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

todos = []


class Todo(BaseModel):
    id: int
    description: str
    completed: bool | None = False


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    context = {"todos": todos, "count": todo_count()}
    return templates.TemplateResponse(request, "index.html", context)


@app.get("/todos", response_class=HTMLResponse)
async def get_todos(request: Request, count: str):
    context = {"todos": filter_todos(count), "count": todo_count()}
    return templates.TemplateResponse(request, "responses/get-todos.html", context)


@app.post("/todo", response_class=HTMLResponse)
async def create_todo(request: Request, description: Annotated[str, Form()]):
    todo = Todo(description=description, id=int(time.time_ns() / 1000))
    todos.append(todo)

    context = {"todos": todos, "count": todo_count(), "todo": todo}
    return templates.TemplateResponse(request, "responses/create-todo.html", context)


@app.patch("/todo/{id}", response_class=HTMLResponse)
async def update_todo(
    request: Request,
    id: int,
    description: Annotated[str | None, Form()] = None,
    completed: Annotated[bool | None, Form()] = None,
):
    [index] = [i for (i, item) in enumerate(todos) if item.id == id]

    if description is not None:
        todos[index].description = description

    if completed is not None:
        todos[index].completed = not todos[index].completed

    context = {"todos": todos, "count": todo_count(), "todo": todos[index]}
    return templates.TemplateResponse(request, "responses/update-todo.html", context)


@app.delete("/todo/{id}", response_class=HTMLResponse)
async def delete_todo(request: Request, id: int):
    [index] = [i for (i, item) in enumerate(todos) if item.id == id]
    todos.pop(index)

    context = {"todos": todos, "count": todo_count()}
    return templates.TemplateResponse(request, "responses/delete-todo.html", context)


@app.get("/todo/{id}/edit", response_class=HTMLResponse)
async def edit_todo(request: Request, id: int):
    [index] = [i for (i, item) in enumerate(todos) if item.id == id]

    context = {"todos": todos, "count": todo_count(), "todo": todos[index]}
    return templates.TemplateResponse(request, "responses/edit-todo.html", context)


@app.put("/todos/completed", response_class=HTMLResponse)
async def mark_all_completed(request: Request, completed: Annotated[bool, Form()]):
    for todo in todos:
        todo.completed = completed

    context = {"todos": todos, "count": todo_count()}
    return templates.TemplateResponse(
        request, "responses/mark-all-completed.html", context
    )


@app.delete("/todos/completed", response_class=HTMLResponse)
async def delete_all_completed(request: Request):
    todos[:] = [todo for todo in todos if todo.completed == False]
    context = {"todos": todos, "count": todo_count()}
    time.sleep(2)
    return templates.TemplateResponse(
        request, "responses/delete-all-completed.html", context
    )


@app.put("/todo/{id}/cancel-edit", response_class=HTMLResponse)
def cancel_edit(request: Request, id: int):
    [index] = [i for (i, item) in enumerate(todos) if item.id == id]

    context = {"todos": todos, "todo": todos[index], "count": todo_count()}
    return templates.TemplateResponse(request, "responses/cancel-edit.html", context)


def todo_count() -> dict[str, int]:
    return {
        "total": len([todo for todo in todos]),
        "active": len([todo for todo in todos if todo.completed == False]),
        "completed": len([todo for todo in todos if todo.completed == True]),
    }


def filter_todos(filter: str) -> list[Todo]:
    if filter == "active":
        return [todo for todo in todos if todo.completed == False]
    elif filter == "completed":
        return [todo for todo in todos if todo.completed == True]
    else:
        return todos
