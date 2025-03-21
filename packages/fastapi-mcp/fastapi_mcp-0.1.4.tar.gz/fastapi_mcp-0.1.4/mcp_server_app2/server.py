import json
import requests
from typing import TypeVar, Set, Any, Dict, List, Optional, Tuple, Union, get_args, get_origin
from datetime import datetime
from uuid import UUID
import mcp
from pydantic import BaseModel, Field

# NoneType definition for Union[X, None] annotations
NoneType = type(None)

# Define PydanticUndefined for required fields
PydanticUndefined = ...

def serialize_model(model):
    # Handle Pydantic v1 and v2 models
    if hasattr(model, 'model_dump_json'):  # Pydantic v2
        return json.loads(model.model_dump_json())
    elif hasattr(model, 'json'):  # Pydantic v1
        return json.loads(model.json())
    # Try as dataclass or dict
    try:
        if is_dataclass(model):
            return asdict(model)
        # Handle dicts, lists, etc.
        return model
    except Exception:
        # Last resort: try __dict__
        return model.__dict__

from enum import Enum, auto

# API enum types
class Priority(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

class Status(Enum):
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'

# API Pydantic models
class Category(BaseModel):
    name: str = PydanticUndefined
    description: Optional[str]
    color: Optional[str]
    id: int = PydanticUndefined
    created_at: datetime = PydanticUndefined

class CategoryCreate(BaseModel):
    name: str = PydanticUndefined
    description: Optional[str]
    color: Optional[str]

class Todo(BaseModel):
    title: str = PydanticUndefined
    description: Optional[str]
    priority: Priority = 'Priority.MEDIUM'
    status: Status = 'Status.TODO'
    due_date: Optional[datetime]
    category_id: Optional[int]
    tags: List[str] = PydanticUndefined
    id: UUID = PydanticUndefined
    created_at: datetime = PydanticUndefined
    updated_at: Optional[datetime]

class TodoCreate(BaseModel):
    title: str = PydanticUndefined
    description: Optional[str]
    priority: Priority = 'Priority.MEDIUM'
    status: Status = 'Status.TODO'
    due_date: Optional[datetime]
    category_id: Optional[int]
    tags: List[str] = PydanticUndefined

class TodoBase(BaseModel):
    title: str = PydanticUndefined
    description: Optional[str]
    priority: Priority = 'Priority.MEDIUM'
    status: Status = 'Status.TODO'
    due_date: Optional[datetime]
    category_id: Optional[int]
    tags: List[str] = PydanticUndefined

# API tools
@mcp.tool(name="health_check", description="Simple health check endpoint to verify the API is running")
async def health_check():
    """
    Simple health check endpoint to verify the API is running
    """
    url = "http://localhost:8000/health"
    params = None
    data = None
    response = requests.get(url, params=params, json=data)
    return response.json()

@mcp.tool(name="create_category", description="Create a new todo category")
async def create_category(category: CategoryCreate):
    """
    Create a new todo category
    """
    url = "http://localhost:8000/categories"
    params = None
    data = serialize_model(category)
    response = requests.post(url, params=params, json=data)
    return response.json()

@mcp.tool(name="list_categories", description="Get a list of all categories")
async def list_categories():
    """
    Get a list of all categories
    """
    url = "http://localhost:8000/categories"
    params = None
    data = None
    response = requests.get(url, params=params, json=data)
    return response.json()

@mcp.tool(name="get_category_by_id", description="Get a specific category by ID")
async def get_category_by_id(category_id: Path = PydanticUndefined):
    """
    Get a specific category by ID
    """
    url = f"http://localhost:8000/categories/{category_id}"
    params = None
    data = None
    response = requests.get(url, params=params, json=data)
    return response.json()

@mcp.tool(name="create_todo", description="Create a new todo item")
async def create_todo(todo: TodoCreate):
    """
    Create a new todo item
    """
    url = "http://localhost:8000/todos"
    params = None
    data = serialize_model(todo)
    response = requests.post(url, params=params, json=data)
    return response.json()

@mcp.tool(name="list_todos", description="Get a list of todos with optional filtering")
async def list_todos(skip: Query = 0, limit: Query = 10, status: Query = None, priority: Query = None, category_id: Query = None):
    """
    Get a list of todos with optional filtering
    """
    url = "http://localhost:8000/todos"
    params = {}
    params['skip'] = skip
    params['limit'] = limit
    params['status'] = status
    params['priority'] = priority
    params['category_id'] = category_id
    data = None
    response = requests.get(url, params=params, json=data)
    return response.json()

@mcp.tool(name="get_todo", description="Get a specific todo by ID")
async def get_todo(todo_id: UUID):
    """
    Get a specific todo by ID
    """
    url = f"http://localhost:8000/todos/{todo_id}"
    params = None
    data = None
    response = requests.get(url, params=params, json=data)
    return response.json()

@mcp.tool(name="update_todo", description="Update an existing todo")
async def update_todo(todo_id: UUID, todo: TodoBase):
    """
    Update an existing todo
    """
    url = f"http://localhost:8000/todos/{todo_id}"
    params = None
    data = serialize_model(todo)
    response = requests.put(url, params=params, json=data)
    return response.json()

@mcp.tool(name="delete_todo", description="Delete a todo")
async def delete_todo(todo_id: UUID):
    """
    Delete a todo
    """
    url = f"http://localhost:8000/todos/{todo_id}"
    params = None
    data = None
    response = requests.delete(url, params=params, json=data)
    return response.json()

@mcp.tool(name="get_todos_by_status", description="Get all todos with a specific status")
async def get_todos_by_status(status: Status):
    """
    Get all todos with a specific status
    """
    url = f"http://localhost:8000/todos/by-status/{status}"
    params = None
    data = None
    response = requests.get(url, params=params, json=data)
    return response.json()

@mcp.tool(name="get_todos_by_priority", description="Get all todos with a specific priority")
async def get_todos_by_priority(priority: Priority):
    """
    Get all todos with a specific priority
    """
    url = f"http://localhost:8000/todos/by-priority/{priority}"
    params = None
    data = None
    response = requests.get(url, params=params, json=data)
    return response.json()

@mcp.tool(name="update_todo_status", description="Update just the status of a todo")
async def update_todo_status(todo_id: UUID, status: Status):
    """
    Update just the status of a todo
    """
    url = f"http://localhost:8000/todos/{todo_id}/status"
    params = {}
    params['status'] = status
    data = None
    response = requests.put(url, params=params, json=data)
    return response.json()

@mcp.tool(name="get_todos_by_category", description="Get all todos belonging to a specific category")
async def get_todos_by_category(category_id: Path = PydanticUndefined, status: Optional[Status] = None):
    """
    Get all todos belonging to a specific category
    """
    url = f"http://localhost:8000/categories/{category_id}/todos"
    params = {}
    params['status'] = status
    data = None
    response = requests.get(url, params=params, json=data)
    return response.json()
