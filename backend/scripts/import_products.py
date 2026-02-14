"""
Import the 46 core products from CSV into the products table.

Usage:
    cd backend
    venv/bin/python scripts/import_products.py
"""

import csv
import sys
import os

# Add parent dir so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.product import Product

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "processed", "core_products.csv"
)


def main():
    db = SessionLocal()

    # Check if products already exist
    existing = db.query(Product).count()
    if existing > 0:
        print(f"Already {existing} products in database. Skipping import.")
        print("To re-import, delete existing products first:")
        print("  psql -d sloth -c \"DELETE FROM products;\"")
        db.close()
        return

    # Read CSV
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Importing {len(rows)} products from {CSV_PATH}...")

    for row in rows:
        product = Product(
            name=row["name"],
            brand=row["brand"] if row["brand"] else None,
            category=row["category"],
            package_size=float(row["package_size"]),
            unit=row["unit"],
            ean=row["ean"] if row["ean"] else None,
            notes=row["notes"] if row["notes"] else None,
        )
        db.add(product)

    db.commit()

    # Verify
    count = db.query(Product).count()
    print(f"Done! {count} products in database.")

    # Show by category
    from sqlalchemy import func
    cats = (
        db.query(Product.category, func.count(Product.id))
        .group_by(Product.category)
        .order_by(func.count(Product.id).desc())
        .all()
    )
    print("\nProducts by category:")
    for cat, cnt in cats:
        print(f"  {cat}: {cnt}")

    db.close()


if __name__ == "__main__":
    main()
