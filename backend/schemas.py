"""
schemas.py — Pydantic models for request validation and response formatting.
FastAPI uses these to automatically validate incoming JSON and document the API.
You already know this from your FastAPI work at Jio!
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


# ── REQUEST SCHEMAS (what the client sends) ───────────────────────────────────

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Product name")
    category: str = Field(..., min_length=1, max_length=50)
    quantity: int = Field(..., ge=0, description="Initial quantity (0 or more)")
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    low_stock_threshold: int = Field(default=10, ge=1, description="Alert when stock drops to this level")

    @validator("name", "category")
    def no_empty_strings(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()


class StockUpdate(BaseModel):
    action: str = Field(..., description="Must be 'add' or 'remove'")
    quantity: int = Field(..., gt=0, description="Units to add or remove")
    note: Optional[str] = Field(None, max_length=200, description="Optional reason for the change")

    @validator("action")
    def validate_action(cls, v):
        if v not in ["add", "remove"]:
            raise ValueError("Action must be 'add' or 'remove'")
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[float] = Field(None, gt=0)
    low_stock_threshold: Optional[int] = Field(None, ge=1)


# ── RESPONSE SCHEMAS (what the server returns) ────────────────────────────────

class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    quantity: int
    price: float
    low_stock_threshold: int
    is_low_stock: bool = False      # Computed field — not stored in DB
    is_out_of_stock: bool = False   # Computed field

    class Config:
        from_attributes = True  # Lets Pydantic read from SQLAlchemy model objects


class StockHistoryResponse(BaseModel):
    id: int
    product_id: int
    action: str
    quantity_changed: int
    quantity_before: int
    quantity_after: int
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total_products: int
    total_stock: int
    low_stock_count: int
    out_of_stock_count: int
    total_categories: int
