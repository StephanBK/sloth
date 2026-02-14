"""
Product Models - Product, ProductAvailability, ProductAlternative

These tables store the ~46 core products used across all meal plans,
which stores carry them, and substitution options.
"""

import uuid
from datetime import datetime, date
from sqlalchemy import (
    String, Integer, Float, DateTime, Date, ForeignKey, Text,
    Boolean, Index, CheckConstraint, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Product(Base):
    """
    A product from the meal plans (e.g. "REWE Beste Wahl High Protein Quarkcreme").

    46 core products extracted from the diet plans, with nutritional info
    and barcodes for shopping list generation.
    """
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # Product identification
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str] = mapped_column(String(255), nullable=True)
    ean: Mapped[str] = mapped_column(String(13), nullable=True)  # barcode

    # Categorization
    category: Mapped[str] = mapped_column(String(100), nullable=False)

    # Package info
    package_size: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)  # g, ml, piece

    # Nutritional data per 100g/100ml
    calories_per_100g: Mapped[float] = mapped_column(Float, nullable=True)
    protein_per_100g: Mapped[float] = mapped_column(Float, nullable=True)
    carbs_per_100g: Mapped[float] = mapped_column(Float, nullable=True)
    fat_per_100g: Mapped[float] = mapped_column(Float, nullable=True)
    fiber_per_100g: Mapped[float] = mapped_column(Float, nullable=True)
    sugar_per_100g: Mapped[float] = mapped_column(Float, nullable=True)
    salt_per_100g: Mapped[float] = mapped_column(Float, nullable=True)

    # Notes
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    availability: Mapped[list["ProductAvailability"]] = relationship(
        "ProductAvailability",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    # Alternatives where this product is the original
    alternatives: Mapped[list["ProductAlternative"]] = relationship(
        "ProductAlternative",
        back_populates="original_product",
        foreign_keys="ProductAlternative.original_product_id",
        cascade="all, delete-orphan",
    )
    # Ingredients that link to this product
    ingredients: Mapped[list["Ingredient"]] = relationship(
        "Ingredient",
        back_populates="product",
    )

    def __repr__(self) -> str:
        return f"<Product {self.name} ({self.brand})>"


class ProductAvailability(Base):
    """Which supermarket chains carry which products."""
    __tablename__ = "product_availability"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    store_chain: Mapped[str] = mapped_column(String(100), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    last_verified: Mapped[date] = mapped_column(Date, default=date.today, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="availability")

    __table_args__ = (
        UniqueConstraint("product_id", "store_chain", name="uq_product_store"),
    )

    def __repr__(self) -> str:
        return f"<ProductAvailability {self.store_chain} {'Y' if self.is_available else 'N'}>"


class ProductAlternative(Base):
    """Substitution options when a product is unavailable."""
    __tablename__ = "product_alternatives"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    original_product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    alternative_product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=1)  # 1 = best

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    original_product: Mapped["Product"] = relationship(
        "Product",
        back_populates="alternatives",
        foreign_keys=[original_product_id],
    )
    alternative_product: Mapped["Product"] = relationship(
        "Product",
        foreign_keys=[alternative_product_id],
    )

    __table_args__ = (
        CheckConstraint(
            "original_product_id != alternative_product_id",
            name="ck_different_products",
        ),
    )

    def __repr__(self) -> str:
        return f"<ProductAlternative priority={self.priority}>"
