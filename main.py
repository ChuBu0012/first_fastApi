from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enum import Enum
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.future import select
from sqlalchemy.orm import Session

# Database setup
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

# Enum and Pydantic model
class TodoStatus(str, Enum):
    pending = "pending"
    in_process = "in_process"
    completed = "completed"

class TodoBase(BaseModel):
    name: str | None = None
    detail: str | None = None
    status: TodoStatus | None = None

class TodoCreate(TodoBase):
    pass

class TodoDB(TodoBase):
    id: int

    class Config:
        orm_mode = True

# SQLAlchemy model
class TodoModel(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    detail = Column(String, index=True, nullable=True)
    status = Column(SQLAlchemyEnum(TodoStatus), default=TodoStatus.pending)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.post("/createTodo", response_model=TodoDB, status_code=status.HTTP_201_CREATED)
async def create_todo(new_todo: TodoCreate, db: Session = Depends(get_db)):
    todo = TodoModel(**new_todo.dict())
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

@app.get("/getTodos", response_model=List[TodoDB], status_code=status.HTTP_200_OK)
async def get_todos(db: Session = Depends(get_db)):
    todos = db.execute(select(TodoModel)).scalars().all()
    return todos

@app.get("/getTodos/{todo_id}", response_model=TodoDB, status_code=status.HTTP_200_OK)
async def get_todo_by_id(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(TodoModel, todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo

@app.put("/updateTodo/{todo_id}", response_model=TodoDB, status_code=status.HTTP_200_OK)
async def update_todo(todo_id: int, todo_data: TodoBase, db: Session = Depends(get_db)):
    todo = db.get(TodoModel, todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    for key, value in todo_data.dict(exclude_unset=True).items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo

@app.delete("/deleteTodo/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(TodoModel, todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": f"Deleted Todo with id {todo_id}."}
