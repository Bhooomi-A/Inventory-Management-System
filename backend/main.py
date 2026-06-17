"""
main.py — The FastAPI application entry point.
Run with: uvicorn main:app --reload --port 5000

This is very similar to what you built at Jio with FastAPI CRUD!
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

import models
import schemas
from database import engine, get_db

# ── CREATE TABLES ─────────────────────────────────────────────────────────────
# This creates all tables defined in models.py if they don't exist yet
models.Base.metadata.create_all(bind=engine)

# ── FASTAPI APP ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="StockSense Inventory API",
    description="Inventory Management System — Built with FastAPI + SQLite",
    version="1.0.0"
)

# ── CORS MIDDLEWARE ───────────────────────────────────────────────────────────
# Allows our HTML frontend (on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace * with the actual frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── SEED DATA HELPER ──────────────────────────────────────────────────────────
def seed_sample_data(db: Session):
    """Add sample products on first run so the app isn't empty."""
    if db.query(models.Product).count() == 0:
        sample_products = [
            models.Product(name="Wireless Mouse",     category="Electronics", quantity=45, price=599.99, low_stock_threshold=10),
            models.Product(name="USB-C Cable",         category="Electronics", quantity=8,  price=149.50, low_stock_threshold=15),
            models.Product(name="Notebook A4",         category="Stationery",  quantity=120,price=49.00,  low_stock_threshold=20),
            models.Product(name="Ball Pen Blue",       category="Stationery",  quantity=5,  price=10.00,  low_stock_threshold=25),
            models.Product(name="Hand Sanitizer",      category="Health",      quantity=30, price=89.00,  low_stock_threshold=10),
            models.Product(name="Face Mask (50 pack)", category="Health",      quantity=3,  price=199.00, low_stock_threshold=10),
            models.Product(name="Coffee Mug",          category="Kitchen",     quantity=22, price=299.00, low_stock_threshold=5),
            models.Product(name="Sticky Notes",        category="Stationery",  quantity=60, price=35.00,  low_stock_threshold=15),
        ]
        db.add_all(sample_products)
        db.commit()


def enrich_product(p: models.Product) -> dict:
    """Add computed fields (is_low_stock, is_out_of_stock) before returning."""
    return {
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "quantity": p.quantity,
        "price": p.price,
        "low_stock_threshold": p.low_stock_threshold,
        "is_low_stock": p.quantity <= p.low_stock_threshold,
        "is_out_of_stock": p.quantity == 0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    """Runs once when the server starts — seeds sample data."""
    db = next(get_db())
    seed_sample_data(db)


# ── GET /api/products — List all products ────────────────────────────────────
@app.get("/api/products", tags=["Products"])
def get_products(
    search: Optional[str] = Query(None, description="Search by name or category"),
    category: Optional[str] = Query(None),
    low_stock: Optional[bool] = Query(None, alias="lowStock"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Product)

    if search:
        query = query.filter(
            models.Product.name.ilike(f"%{search}%") |
            models.Product.category.ilike(f"%{search}%")
        )
    if category:
        query = query.filter(models.Product.category == category)
    if low_stock:
        query = query.filter(models.Product.quantity <= models.Product.low_stock_threshold)

    products = query.order_by(models.Product.name).all()
    return {"success": True, "data": [enrich_product(p) for p in products]}


# ── GET /api/stats — Dashboard summary ───────────────────────────────────────
@app.get("/api/stats", tags=["Dashboard"])
def get_stats(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return {
        "success": True,
        "data": {
            "total_products":    len(products),
            "total_stock":       sum(p.quantity for p in products),
            "low_stock_count":   sum(1 for p in products if p.quantity <= p.low_stock_threshold),
            "out_of_stock_count":sum(1 for p in products if p.quantity == 0),
            "total_categories":  len(set(p.category for p in products)),
        }
    }


# ── POST /api/products — Add a new product ───────────────────────────────────
@app.post("/api/products", status_code=201, tags=["Products"])
def add_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    # Check for duplicate name (case-insensitive)
    existing = db.query(models.Product).filter(
        models.Product.name.ilike(payload.name)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="A product with this name already exists")

    product = models.Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"success": True, "message": "Product added!", "data": enrich_product(product)}


# ── PATCH /api/products/{id}/stock — Update stock ────────────────────────────
@app.patch("/api/products/{product_id}/stock", tags=["Products"])
def update_stock(product_id: int, payload: schemas.StockUpdate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    qty_before = product.quantity

    if payload.action == "add":
        product.quantity += payload.quantity
    else:
        # ── PREVENT NEGATIVE STOCK ─────────────────────────────────────────
        if product.quantity - payload.quantity < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot remove {payload.quantity} units. Only {product.quantity} in stock."
            )
        product.quantity -= payload.quantity

    # Log to stock history (audit trail)
    history_entry = models.StockHistory(
        product_id       = product.id,
        action           = payload.action.upper(),
        quantity_changed = payload.quantity,
        quantity_before  = qty_before,
        quantity_after   = product.quantity,
        note             = payload.note
    )
    db.add(history_entry)
    db.commit()
    db.refresh(product)
    return {"success": True, "message": "Stock updated!", "data": enrich_product(product)}


# ── PUT /api/products/{id} — Edit product details ────────────────────────────
@app.put("/api/products/{product_id}", tags=["Products"])
def update_product(product_id: int, payload: schemas.ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = payload.dict(exclude_unset=True)  # Only update fields that were sent
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return {"success": True, "message": "Product updated!", "data": enrich_product(product)}


# ── DELETE /api/products/{id} — Delete a product ─────────────────────────────
@app.delete("/api/products/{product_id}", tags=["Products"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete history first (foreign key constraint)
    db.query(models.StockHistory).filter(models.StockHistory.product_id == product_id).delete()
    db.delete(product)
    db.commit()
    return {"success": True, "message": "Product deleted"}


# ── GET /api/products/{id}/history — Stock history ───────────────────────────
@app.get("/api/products/{product_id}/history", tags=["Products"])
def get_history(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    history = (
        db.query(models.StockHistory)
        .filter(models.StockHistory.product_id == product_id)
        .order_by(models.StockHistory.created_at.desc())
        .limit(20)
        .all()
    )
    return {"success": True, "data": history}
