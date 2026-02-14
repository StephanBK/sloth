"""
Add store availability for products.

Most products in the meal plans are from REWE (REWE Beste Wahl, REWE Bio, ja! brands).
This script marks which stores carry each product based on brand.

Usage:
    cd backend
    venv/bin/python scripts/add_store_availability.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.product import Product, ProductAvailability

# Brand -> which stores carry them
BRAND_STORES = {
    "REWE Beste Wahl": ["REWE"],
    "REWE Bio": ["REWE"],
    "REWE": ["REWE"],
    "ja!": ["REWE"],  # ja! is REWE's budget brand
    "Wilhelm Brandenburg": ["REWE"],  # REWE exclusive brand
    # National brands available at multiple stores
    "Frosta": ["REWE", "Edeka", "Kaufland"],
    "Iglo": ["REWE", "Edeka", "Kaufland"],
    "McCain": ["REWE", "Edeka", "Kaufland", "Lidl"],
    "Dr. Oetker": ["REWE", "Edeka", "Kaufland", "Lidl", "Aldi"],
    "Ben's Original": ["REWE", "Edeka", "Kaufland"],
    "RUF": ["REWE", "Edeka", "Kaufland"],
    "Weetabix": ["REWE", "Edeka"],
    "Wasa": ["REWE", "Edeka", "Kaufland", "Lidl"],
    "Like Meat": ["REWE", "Edeka"],
    "Rügenwalder Mühle": ["REWE", "Edeka", "Kaufland", "Lidl"],
    "Salakis": ["REWE", "Edeka", "Kaufland"],
    # Generic items available everywhere
    "Generic": ["REWE", "Edeka", "Kaufland", "Lidl", "Aldi"],
}


def main():
    db = SessionLocal()

    # Check if we already have data
    existing = db.query(ProductAvailability).count()
    if existing > 0:
        print(f"Already {existing} availability records. Clearing and re-adding...")
        db.query(ProductAvailability).delete()
        db.commit()

    products = db.query(Product).all()
    added = 0

    for product in products:
        stores = BRAND_STORES.get(product.brand, [])
        if not stores:
            print(f"  No store mapping for brand: {product.brand} ({product.name})")
            continue

        for store in stores:
            avail = ProductAvailability(
                product_id=product.id,
                store_chain=store,
                is_available=True,
            )
            db.add(avail)
            added += 1

    db.commit()

    # Summary
    print(f"\nAdded {added} availability records for {len(products)} products")

    from sqlalchemy import func
    store_counts = (
        db.query(ProductAvailability.store_chain, func.count(ProductAvailability.id))
        .filter(ProductAvailability.is_available == True)
        .group_by(ProductAvailability.store_chain)
        .order_by(func.count(ProductAvailability.id).desc())
        .all()
    )
    print("\nProducts by store:")
    for store, count in store_counts:
        print(f"  {store}: {count} products")

    db.close()


if __name__ == "__main__":
    main()
