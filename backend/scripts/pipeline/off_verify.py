"""
Verify the OFF import integrity.

Checks for duplicate EANs, broken relationships, outlier nutrition values,
and prints summary statistics.

Usage:
    cd backend
    python scripts/pipeline/off_verify.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import func, text
from app.database import SessionLocal
from app.models.product import Product, ProductSourceLink
from app.models.meal_plan import Ingredient


def main():
    db = SessionLocal()

    print("="*60)
    print("OFF Import Verification Report")
    print("="*60)

    # --- Product counts by source ---
    print("\n1. Products by data_source:")
    rows = (
        db.query(Product.data_source, func.count(Product.id))
        .group_by(Product.data_source)
        .order_by(Product.data_source)
        .all()
    )
    total = 0
    for source, count in rows:
        print(f"   {source:12s}: {count:,}")
        total += count
    print(f"   {'TOTAL':12s}: {total:,}")

    # --- Curated products ---
    curated = db.query(func.count(Product.id)).filter(Product.is_curated == True).scalar()
    print(f"\n2. Curated products: {curated}")

    # --- Products with nutrition data ---
    with_nutrition = (
        db.query(func.count(Product.id))
        .filter(Product.calories_per_100g.isnot(None))
        .scalar()
    )
    print(f"   Products with calories: {with_nutrition:,} / {total:,}")

    # --- Duplicate EAN check ---
    print("\n3. Duplicate EAN check:")
    dup_eans = (
        db.query(Product.ean, func.count(Product.id).label("cnt"))
        .filter(Product.ean.isnot(None))
        .group_by(Product.ean)
        .having(func.count(Product.id) > 1)
        .order_by(text("cnt DESC"))
        .limit(10)
        .all()
    )
    if dup_eans:
        print(f"   WARNING: Found {len(dup_eans)} duplicate EANs (showing top 10):")
        for ean, cnt in dup_eans:
            print(f"     EAN {ean}: {cnt} products")
    else:
        print("   OK - No duplicate EANs found.")

    # --- Source links ---
    link_count = db.query(func.count(ProductSourceLink.id)).scalar()
    print(f"\n4. Product source links: {link_count:,}")
    if link_count > 0:
        by_method = (
            db.query(ProductSourceLink.match_method, func.count(ProductSourceLink.id))
            .group_by(ProductSourceLink.match_method)
            .all()
        )
        for method, cnt in by_method:
            print(f"   {method or 'unknown':15s}: {cnt:,}")

    # --- Ingredient links integrity ---
    print("\n5. Ingredient-Product links:")
    total_ingredients = db.query(func.count(Ingredient.id)).scalar()
    linked_ingredients = (
        db.query(func.count(Ingredient.id))
        .filter(Ingredient.product_id.isnot(None))
        .scalar()
    )
    orphan_links = (
        db.query(func.count(Ingredient.id))
        .filter(Ingredient.product_id.isnot(None))
        .filter(
            ~Ingredient.product_id.in_(
                db.query(Product.id)
            )
        )
        .scalar()
    )
    print(f"   Total ingredients: {total_ingredients:,}")
    print(f"   Linked to products: {linked_ingredients:,}")
    if orphan_links > 0:
        print(f"   WARNING: {orphan_links} orphaned product_id references!")
    else:
        print(f"   OK - No orphaned references.")

    # --- Nutrition outlier check ---
    print("\n6. Nutrition outlier check:")
    outliers_high_kcal = (
        db.query(func.count(Product.id))
        .filter(Product.calories_per_100g > 1000)
        .scalar()
    )
    outliers_zero = (
        db.query(func.count(Product.id))
        .filter(Product.calories_per_100g == 0)
        .scalar()
    )
    print(f"   Products > 1000 kcal/100g: {outliers_high_kcal:,} (oils, nuts, etc. are normal)")
    print(f"   Products = 0 kcal/100g: {outliers_zero:,} (water, spices may be OK)")

    # --- Category distribution ---
    print("\n7. Category distribution:")
    cats = (
        db.query(Product.category, func.count(Product.id))
        .group_by(Product.category)
        .order_by(func.count(Product.id).desc())
        .all()
    )
    for cat, cnt in cats:
        print(f"   {cat:30s}: {cnt:,}")

    # --- Sample products from OFF ---
    print("\n8. Sample OFF products (5 random):")
    samples = (
        db.query(Product)
        .filter(Product.data_source == "off")
        .order_by(func.random())
        .limit(5)
        .all()
    )
    for p in samples:
        print(f"   {p.name} | {p.brand or '-'} | {p.category} | {p.calories_per_100g} kcal | EAN:{p.ean or '-'}")

    print(f"\n{'='*60}")
    db.close()


if __name__ == "__main__":
    main()
