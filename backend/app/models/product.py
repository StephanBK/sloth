"""
Product Models - Product, ProductAvailability, ProductAlternative, ProductSourceLink

Product catalog with multi-source data pipeline support.
Sources: manual (curated), off (Open Food Facts), bls (Bundeslebensmittelschlüssel).
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
    A grocery product with nutritional data.

    Products come from multiple sources: manually curated (46 core products),
    Open Food Facts bulk import, and BLS scientific database.
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

    # Package info (nullable for bulk imports that lack packaging data)
    package_size: Mapped[float] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=True)  # g, ml, piece

    # Nutritional data per 100g/100ml
    calories_per_100g: Mapped[float] = mapped_column(Float, nullable=True)
    protein_per_100g: Mapped[float] = mapped_column(Float, nullable=True)
    carbs_per_100g: Mapped[float] = mapped_column(Float, nullable=True)
    fat_per_100g: Mapped[float] = mapped_column(Float, nullable=True)
    fiber_per_100g: Mapped[float] = mapped_column(Float, nullable=True)
    sugar_per_100g: Mapped[float] = mapped_column(Float, nullable=True)
    salt_per_100g: Mapped[float] = mapped_column(Float, nullable=True)

    # Data provenance
    data_source: Mapped[str] = mapped_column(
        String(50), nullable=False, default="manual"
    )  # "manual", "off", "bls"
    data_confidence: Mapped[float] = mapped_column(Float, nullable=True)  # 0.0-1.0
    is_curated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # External identifiers
    off_id: Mapped[str] = mapped_column(String(50), nullable=True)
    bls_code: Mapped[str] = mapped_column(String(20), nullable=True)

    # Quality/display fields
    nutriscore_grade: Mapped[str] = mapped_column(String(1), nullable=True)  # a-e
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    image_thumb_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # Notes
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_synced_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

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
    # Source links for cross-referencing across data sources
    source_links: Mapped[list["ProductSourceLink"]] = relationship(
        "ProductSourceLink",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_products_data_source", "data_source"),
        Index("idx_products_off_id", "off_id"),
        Index("idx_products_bls_code", "bls_code"),
    )

    def __repr__(self) -> str:
        return f"<Product {self.name} ({self.brand}) src={self.data_source}>"


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


class ProductSourceLink(Base):
    """Cross-reference when a product is matched across multiple data sources."""
    __tablename__ = "product_source_links"

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
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # "off", "bls"
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)
    external_data: Mapped[str] = mapped_column(Text, nullable=True)  # raw JSON snapshot
    matched_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    match_method: Mapped[str] = mapped_column(String(50), nullable=True)  # "ean_exact", "fuzzy_name"
    match_confidence: Mapped[float] = mapped_column(Float, nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="source_links")

    def __repr__(self) -> str:
        return f"<ProductSourceLink {self.source}:{self.external_id}>"
