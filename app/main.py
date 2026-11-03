import os
from itertools import count

from fastapi import FastAPI, HTTPException, Query
from app.models import HealthResponse, Item, ItemCreate

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

app = FastAPI(
    title="Items API",
    description="A sample FastAPI service packaged with Docker.",
    version=APP_VERSION,
)

# In-memory store. Replace with a real database for anything beyond a demo:
# every restart of the container wipes this clean.
_items: dict[int, Item] = {}
_next_id = count(1)


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    """Friendly landing route pointing at the interactive docs."""
    return {"message": "Items API is running", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health() -> HealthResponse:
    """Liveness probe used by Docker HEALTHCHECK and load balancers."""
    return HealthResponse(status="ok", version=APP_VERSION)


@app.get("/items", response_model=list[Item], tags=["items"])
def list_items(
    in_stock: bool | None = Query(None, description="Filter by stock availability"),
    limit: int = Query(50, ge=1, le=200),
) -> list[Item]:
    """Return items, optionally filtered by availability."""
    items = list(_items.values())
    if in_stock is not None:
        items = [item for item in items if item.in_stock == in_stock]
    return items[:limit]


@app.get("/items/{item_id}", response_model=Item, tags=["items"])
def get_item(item_id: int) -> Item:
    """Return a single item, or 404 if it does not exist."""
    item = _items.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item


@app.post("/items", response_model=Item, status_code=201, tags=["items"])
def create_item(payload: ItemCreate) -> Item:
    """Create an item; the server assigns the id."""
    item = Item(id=next(_next_id), **payload.model_dump())
    _items[item.id] = item
    return item


@app.delete("/items/{item_id}", status_code=204, tags=["items"])
def delete_item(item_id: int) -> None:
    """Delete an item, or 404 if it does not exist."""
    if _items.pop(item_id, None) is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")