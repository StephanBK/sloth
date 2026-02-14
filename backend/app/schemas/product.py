"""
Product Schemas - API Response Models for the product catalog.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class ProductResponse(BaseModel):
    """Product returned to the client."""
    id: str
    name: str
    brand: Optional[str] = None
    ean: Optional[str] = None
    category: str
    package_size: float
    unit: str
    calories_per_100g: Optional[float] = None
    protein_per_100g: Optional[float] = None
    carbs_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None
    fiber_per_100g: Optional[float] = None
    sugar_per_100g: Optional[float] = None
    salt_per_100g: Optional[float] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Compact product for list views."""
    id: str
    name: str
    brand: Optional[str] = None
    category: str
    package_size: float
    unit: str

    class Config:
        from_attributes = True


class ProductAvailabilityResponse(BaseModel):
    """Store availability info."""
    id: str
    store_chain: str
    is_available: bool
    last_verified: Optional[date] = None

    class Config:
        from_attributes = True


class ProductDetailResponse(ProductResponse):
    """Full product detail including availability."""
    availability: list[ProductAvailabilityResponse] = []

    class Config:
        from_attributes = True
