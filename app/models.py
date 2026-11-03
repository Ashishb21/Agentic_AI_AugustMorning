from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Payload returned by the liveness probe."""

    status: str
    version: str


class ItemCreate(BaseModel):
    """Fields the client supplies when creating an item."""

    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: float = Field(ge=0)
    in_stock: bool = True


class Item(ItemCreate):
    """A stored item; the id is assigned by the server."""

    id: int
