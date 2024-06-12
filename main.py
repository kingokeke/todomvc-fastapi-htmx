import time
from typing import Annotated
from fastapi import FastAPI, Form, Header, Request
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
async def get_todos(
    request: Request,
    count: str,
    hx_request: Annotated[bool | None, Header()] = None,
):
    if hx_request:
        # Compose and return HTMX response here
        context = {"todos": filter_todos(count), "count": todo_count()}
        return templates.TemplateResponse(request, "responses/get-todos.html", context)
    else:
        # Compose and return JSON response here
        pass


@app.post("/todo", response_class=HTMLResponse)
async def create_todo(
    request: Request,
    description: Annotated[str, Form()],
    hx_request: Annotated[bool | None, Header()] = None,
):
    todo = Todo(description=description, id=int(time.time_ns() / 1000))
    todos.append(todo)

    if hx_request:
        # Compose and return HTMX response here
        context = {"todos": todos, "count": todo_count(), "todo": todo}
        return templates.TemplateResponse(
            request, "responses/create-todo.html", context
        )
    else:
        # Compose and return JSON response here
        pass


@app.patch("/todo/{id}", response_class=HTMLResponse)
async def update_todo(
    request: Request,
    id: int,
    description: Annotated[str | None, Form()] = None,
    completed: Annotated[bool | None, Form()] = None,
    hx_request: Annotated[bool | None, Header()] = None,
):
    [index] = [i for (i, item) in enumerate(todos) if item.id == id]

    if description is not None:
        todos[index].description = description

    if completed is not None:
        todos[index].completed = not todos[index].completed

    if hx_request:
        # Compose and return HTMX response here
        context = {"todos": todos, "count": todo_count(), "todo": todos[index]}
        return templates.TemplateResponse(
            request, "responses/update-todo.html", context
        )
    else:
        # Compose and return JSON response here
        pass


@app.delete("/todo/{id}", response_class=HTMLResponse)
async def delete_todo(
    request: Request,
    id: int,
    hx_request: Annotated[bool | None, Header()] = None,
):
    [index] = [i for (i, item) in enumerate(todos) if item.id == id]
    todos.pop(index)

    if hx_request:
        # Compose and return HTMX response here
        context = {"todos": todos, "count": todo_count()}
        return templates.TemplateResponse(
            request, "responses/delete-todo.html", context
        )
    else:
        # Compose and return JSON response here
        pass


@app.get("/todo/{id}/edit", response_class=HTMLResponse)
async def edit_todo(
    request: Request,
    id: int,
    hx_request: Annotated[bool | None, Header()] = None,
):
    [index] = [i for (i, item) in enumerate(todos) if item.id == id]

    if hx_request:
        # Compose and return HTMX response here
        context = {"todos": todos, "count": todo_count(), "todo": todos[index]}
        return templates.TemplateResponse(request, "responses/edit-todo.html", context)
    else:
        # Compose and return JSON response here
        pass


@app.put("/todos/completed", response_class=HTMLResponse)
async def mark_all_completed(
    request: Request,
    completed: Annotated[bool, Form()],
    hx_request: Annotated[bool | None, Header()] = None,
):
    for todo in todos:
        todo.completed = completed

    if hx_request:
        # Compose and return HTMX response here
        context = {"todos": todos, "count": todo_count()}
        return templates.TemplateResponse(
            request, "responses/mark-all-completed.html", context
        )
    else:
        # Compose and return JSON response here
        pass


@app.delete("/todos/completed", response_class=HTMLResponse)
async def delete_all_completed(
    request: Request,
    hx_request: Annotated[bool | None, Header()] = None,
):
    todos[:] = [todo for todo in todos if todo.completed == False]

    if hx_request:
        # Compose and return HTMX response here
        time.sleep(2)  # Simulate slow network to illustrate HTMX indicator
        context = {"todos": todos, "count": todo_count()}
        return templates.TemplateResponse(
            request, "responses/delete-all-completed.html", context
        )
    else:
        # Compose and return JSON response here
        pass


@app.put("/todo/{id}/cancel-edit", response_class=HTMLResponse)
def cancel_edit(
    request: Request,
    id: int,
    hx_request: Annotated[bool | None, Header()] = None,
):
    [index] = [i for (i, item) in enumerate(todos) if item.id == id]

    if hx_request:
        # Compose and return HTMX response here
        context = {"todos": todos, "todo": todos[index], "count": todo_count()}
        return templates.TemplateResponse(
            request, "responses/cancel-edit.html", context
        )
    else:
        # Compose and return JSON response here
        pass


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
