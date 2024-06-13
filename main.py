import time
import requests
from requests.exceptions import HTTPError
from typing import Annotated
from fastapi import FastAPI, Form, Header, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class Todo(BaseModel):
    id: int
    description: str
    completed: bool | None = False


state: dict[str, any] = {"todos": [], "current_tab": "all"}


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    context = {
        "todos": filter_todos(state["current_tab"]),
        "count": todo_count(),
        "wisdom": get_wisdom_quote(),
        "current_tab": state["current_tab"],
    }
    return templates.TemplateResponse(request, "index.html", context)


@app.get("/todos", response_class=HTMLResponse)
async def get_todos(
    request: Request,
    count: str,
    hx_request: Annotated[bool | None, Header()] = None,
):
    if hx_request:
        # Compose and return HTMX response here
        state["current_tab"] = count
        context = {
            "todos": filter_todos(state["current_tab"]),
            "count": todo_count(),
            "current_tab": state["current_tab"],
        }
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
    state["todos"].append(todo)

    if hx_request:
        # Compose and return HTMX response here
        context = {
            "todos": filter_todos(state["current_tab"]),
            "count": todo_count(),
            "todo": todo,
            "current_tab": state["current_tab"],
        }
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
    [index] = [i for (i, item) in enumerate(state["todos"]) if item.id == id]

    if description is not None:
        state["todos"][index].description = description

    if completed is not None:
        state["todos"][index].completed = not state["todos"][index].completed

    if hx_request:
        # Compose and return HTMX response here
        context = {
            "todos": filter_todos(state["current_tab"]),
            "count": todo_count(),
            "todo": state["todos"][index],
            "current_tab": state["current_tab"],
        }
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
    [index] = [i for (i, item) in enumerate(state["todos"]) if item.id == id]
    state["todos"].pop(index)

    if hx_request:
        # Compose and return HTMX response here
        context = {
            "todos": filter_todos(state["current_tab"]),
            "count": todo_count(),
            "current_tab": state["current_tab"],
        }
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
    [index] = [i for (i, item) in enumerate(state["todos"]) if item.id == id]

    if hx_request:
        # Compose and return HTMX response here
        context = {
            "todos": filter_todos(state["current_tab"]),
            "count": todo_count(),
            "todo": state["todos"][index],
            "current_tab": state["current_tab"],
        }
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
    for todo in state["todos"]:
        todo.completed = completed

    if hx_request:
        # Compose and return HTMX response here
        context = {
            "todos": filter_todos(state["current_tab"]),
            "count": todo_count(),
            "current_tab": state["current_tab"],
        }
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
    state["todos"][:] = [todo for todo in state["todos"] if todo.completed == False]

    if todo_count()["all"] == 0:
        state["current_tab"] = "all"

    if hx_request:
        # Compose and return HTMX response here
        time.sleep(2)  # Simulate slow network to illustrate HTMX indicator
        context = {
            "todos": filter_todos(state["current_tab"]),
            "count": todo_count(),
            "current_tab": state["current_tab"],
        }
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
    [index] = [i for (i, item) in enumerate(state["todos"]) if item.id == id]

    if hx_request:
        # Compose and return HTMX response here
        context = {
            "todos": filter_todos(state["current_tab"]),
            "todo": state["todos"][index],
            "count": todo_count(),
            "current_tab": state["current_tab"],
        }
        return templates.TemplateResponse(
            request, "responses/cancel-edit.html", context
        )
    else:
        # Compose and return JSON response here
        pass


@app.get("/wisdom-quote", response_class=HTMLResponse)
async def wisdom_quote(
    request: Request,
    hx_request: Annotated[bool | None, Header()] = None,
):
    if hx_request:
        # Compose and return HTMX response here
        context = {"wisdom": get_wisdom_quote()}
        return templates.TemplateResponse(request, "wisdom-quote.html", context)
    else:
        # Compose and return JSON response here
        pass


def todo_count() -> dict[str, int]:
    return {
        "all": len([todo for todo in state["todos"]]),
        "active": len([todo for todo in state["todos"] if todo.completed == False]),
        "completed": len([todo for todo in state["todos"] if todo.completed == True]),
    }


def filter_todos(filter: str) -> list[Todo]:
    if filter == "active":
        return [todo for todo in state["todos"] if todo.completed == False]
    elif filter == "completed":
        return [todo for todo in state["todos"] if todo.completed == True]
    else:
        return state["todos"]


def get_wisdom_quote():
    # Demonstrate use case of consuming external API in JSON format
    try:
        response = requests.get("https://api.quotable.io/quotes/random")
        response.raise_for_status()
        wisdom = response.json()[0]
        return {"quote": wisdom["content"], "author": wisdom["author"]}

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
