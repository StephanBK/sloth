"""
Products API Router

Endpoints for browsing the product catalog:
- GET /products - List all products (with filters)
- GET /products/{id} - Get a product with availability info
- GET /products/categories - List all categories
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.database import get_db
from app.models.product import Product
from app.schemas.product import (
    ProductListResponse,
    ProductDetailResponse,
)

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.get("/categories", response_model=list[str])
async def list_categories(db: Session = Depends(get_db)):
    """List all product categories."""
    rows = (
        db.query(Product.category)
        .distinct()
        .order_by(Product.category)
        .all()
    )
    return [r[0] for r in rows]


@router.get("", response_model=list[ProductListResponse])
async def list_products(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name or brand"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    """
    List products with optional filters.

    Examples:
    - GET /products
    - GET /products?category=Dairy+%26+Eggs
    - GET /products?search=quark
    """
    query = db.query(Product)

    if category:
        query = query.filter(Product.category == category)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            Product.name.ilike(pattern) | Product.brand.ilike(pattern)
        )

    query = query.order_by(Product.category, Product.name)
    return query.offset(skip).limit(limit).all()


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: str,
    db: Session = Depends(get_db),
):
    """Get a product with its store availability."""
    product = (
        db.query(Product)
        .options(joinedload(Product.availability))
        .filter(Product.id == product_id)
        .first()
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
