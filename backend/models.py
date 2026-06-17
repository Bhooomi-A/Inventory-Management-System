"""
models.py — Defines the database tables as Python classes.
Each class = one table in SQLite.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Product(Base):
    """
    The 'products' table.
    Stores every product in the inventory.
    """
    __tablename__ = "products"

    id                  = Column(Integer, primary_key=True, index=True)
    name                = Column(String(100), unique=True, nullable=False)
    category            = Column(String(50), nullable=False)
    quantity            = Column(Integer, nullable=False, default=0)
    price               = Column(Float, nullable=False)
    low_stock_threshold = Column(Integer, nullable=False, default=10)
    created_at          = Column(DateTime, server_default=func.now())
    updated_at          = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # One product can have many stock history entries
    history = relationship("StockHistory", back_populates="product")


class StockHistory(Base):
    """
    The 'stock_history' table.
    Every time stock is added or removed, we log it here.
    This is the audit trail — important for real inventory systems.
    """
    __tablename__ = "stock_history"

    id               = Column(Integer, primary_key=True, index=True)
    product_id       = Column(Integer, ForeignKey("products.id"), nullable=False)
    action           = Column(String(10), nullable=False)   # "ADD" or "REMOVE"
    quantity_changed = Column(Integer, nullable=False)
    quantity_before  = Column(Integer, nullable=False)
    quantity_after   = Column(Integer, nullable=False)
    note             = Column(Text, nullable=True)
    created_at       = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="history")
