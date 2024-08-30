from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enum import Enum
from typing import List

origins = ['*']

class TodoStatus(str,Enum):
    pending = "pending"
    in_process = "in_process"
    completed = "completed"

class Todo(BaseModel):
    id : int | None = None
    name : str | None = None
    detail : str | None = None
    status : TodoStatus | None = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

items :List[Todo] = [
    {
        "id": 1,
        "name": "Buy groceries",
        "detail": "Milk, Bread, Eggs",
        "status": "pending"
    },
    {
        "id": 2,
        "name": "Complete homework",
        "detail": "Math exercises",
        "status": "in_process"
    },
    {
        "id": 3,
        "name": "Call mom",
        "detail": None,
        "status": "completed"
    },
    {
        "id": 4,
        "name": "Read a book",
        "detail": "The Catcher in the Rye",
        "status": "pending"
    },
    {
        "id": 5,
        "name": "Prepare dinner",
        "detail": "Pasta and salad",
        "status": "in_process"
    }
]


next_id = 6

@app.post("/createTodo", status_code=status.HTTP_201_CREATED)
async def createTodo(new_todo: Todo):
    global next_id
    new_todo.id = next_id
    new_todo.status = TodoStatus.pending
    items.append(new_todo)
    next_id += 1
    return {"message": "Create Successful!"}

@app.get("/getTodos",status_code=status.HTTP_200_OK)
async def getTodos():
    return items

@app.get("/getTodos/{todo_id}", status_code=status.HTTP_200_OK)
async def getTodosById(todo_id: int):
    todo = next((item for item in items if item['id'] == todo_id), None)
    if todo is not None:
        return todo
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

@app.put("/updateTodo/{todo_id}", status_code=status.HTTP_200_OK)
async def updateTodo(todo_id: int, todo: Todo):
    index = next((i for i, item in enumerate(items) if item['id'] == todo_id), None)
    if index is not None:
        existing_todo = items[index]
        updated_todo = existing_todo.copy()  # Make a copy of the existing todo
        updated_todo.update(todo.dict(exclude_unset=True))  # Update the copy with new values
        items[index] = updated_todo  # Replace the old todo with the updated one
        return {"message": f"Updated Todo with id {todo_id}."}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")


@app.delete("/deleteTodo/{todo_id}",status_code=status.HTTP_200_OK)
async def deleteTodo(todo_id:int):
    index = next((i for i,item in enumerate(items) if item['id'] == todo_id),None)
    if index is not None:
        items.pop(index)
        return {"message": f"Deleted Todo with id {todo_id}."}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")