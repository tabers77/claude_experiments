"""
API routes for the minimal API.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.utils.helpers import generate_id, format_timestamp

router = APIRouter()

# In-memory storage for simplicity
items_db: dict[str, dict] = {}


class ItemCreate(BaseModel):
    name: str
    description: str = ""


class ItemResponse(BaseModel):
    id: str
    name: str
    description: str
    created_at: str


@router.get("/items")
async def list_items() -> list[ItemResponse]:
    """List all items."""
    return [ItemResponse(**item) for item in items_db.values()]


@router.get("/items/{item_id}")
async def get_item(item_id: str) -> ItemResponse:
    """Get a specific item by ID."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse(**items_db[item_id])


@router.post("/items", status_code=201)
async def create_item(item: ItemCreate) -> ItemResponse:
    """Create a new item."""
    item_id = generate_id()
    new_item = {
        "id": item_id,
        "name": item.name,
        "description": item.description,
        "created_at": format_timestamp()
    }
    items_db[item_id] = new_item
    return ItemResponse(**new_item)


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: str):
    """Delete an item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
