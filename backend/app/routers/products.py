"""
Products API Router

Endpoints for browsing the product catalog:
- GET /products - List all products (with filters)
- GET /products/{id} - Get a product with availability info
- GET /products/categories - List all categories
- GET /products/search - Full-text search with confidence ordering
- GET /products/stats - Pipeline statistics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
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


@router.get("/stats")
async def product_stats(db: Session = Depends(get_db)):
    """Pipeline statistics: counts by source, nutrition coverage, etc."""
    total = db.query(func.count(Product.id)).scalar()
    by_source = dict(
        db.query(Product.data_source, func.count(Product.id))
        .group_by(Product.data_source)
        .all()
    )
    curated = (
        db.query(func.count(Product.id))
        .filter(Product.is_curated == True)
        .scalar()
    )
    with_nutrition = (
        db.query(func.count(Product.id))
        .filter(Product.calories_per_100g.isnot(None))
        .scalar()
    )
    return {
        "total": total,
        "by_source": by_source,
        "curated": curated,
        "with_nutrition": with_nutrition,
    }


@router.get("/search", response_model=list[ProductListResponse])
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
):
    """Full-text search across product name and brand, ordered by confidence."""
    pattern = f"%{q}%"
    return (
        db.query(Product)
        .filter(Product.name.ilike(pattern) | Product.brand.ilike(pattern))
        .order_by(
            Product.is_curated.desc(),
            Product.data_confidence.desc().nullslast(),
            Product.name,
        )
        .limit(limit)
        .all()
    )


@router.get("", response_model=list[ProductListResponse])
async def list_products(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name or brand"),
    data_source: Optional[str] = Query(None, description="Filter by data source"),
    curated_only: bool = Query(False, description="Only hand-picked products"),
    min_confidence: float = Query(0.0, ge=0, le=1, description="Minimum data quality"),
    has_nutrition: bool = Query(False, description="Only products with nutrition data"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    """
    List products with optional filters.

    Examples:
    - GET /products
    - GET /products?category=Dairy+%26+Eggs
    - GET /products?search=quark
    - GET /products?curated_only=true
    - GET /products?data_source=off&min_confidence=0.5
    """
    query = db.query(Product)

    if category:
        query = query.filter(Product.category == category)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            Product.name.ilike(pattern) | Product.brand.ilike(pattern)
        )
    if data_source:
        query = query.filter(Product.data_source == data_source)
    if curated_only:
        query = query.filter(Product.is_curated == True)
    if min_confidence > 0:
        query = query.filter(Product.data_confidence >= min_confidence)
    if has_nutrition:
        query = query.filter(Product.calories_per_100g.isnot(None))

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
