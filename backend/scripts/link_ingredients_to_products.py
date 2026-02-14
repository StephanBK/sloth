"""
Link existing meal plan ingredients to product catalog entries.

Matches ingredient.product_name to products.name using prefix/substring matching.

Usage:
    cd backend
    venv/bin/python scripts/link_ingredients_to_products.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.product import Product
from app.models.meal_plan import Ingredient


def build_product_lookup(products):
    """Build a lookup dict: lowered name -> product id."""
    lookup = {}
    for p in products:
        lookup[p.name.lower()] = p.id
    return lookup


# Manual mappings for ingredient names that don't directly match product names
MANUAL_MAPPINGS = {
    "apfel": "Äpfel",
    "banane": "Bananen",
    "magerquark": "ja! Magerquark",
    "olivenöl oder butterschmalz zum braten": "Olivenöl",
}


def normalize(text: str) -> str:
    """Normalize unicode quotes and whitespace."""
    return text.replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')


def find_product_id(ingredient_name: str, lookup: dict, products_by_name: dict) -> str | None:
    """Try to match an ingredient name to a product."""
    name_lower = normalize(ingredient_name).lower().strip()

    # 1. Check manual mappings first
    if name_lower in MANUAL_MAPPINGS:
        mapped = MANUAL_MAPPINGS[name_lower].lower()
        if mapped in lookup:
            return lookup[mapped]

    # 2. Exact match
    if name_lower in lookup:
        return lookup[name_lower]

    # 3. Product name starts with ingredient name (handles truncated names)
    #    e.g. "REWE Beste Wahl High Protein Quarkcreme (" matches "REWE Beste Wahl High Protein Quarkcreme"
    for product_name_lower, product_id in lookup.items():
        if product_name_lower.startswith(name_lower):
            return product_id

    # 4. Ingredient name starts with product name (handles names with extra info)
    #    e.g. "REWE Beste Wahl Chili Sin Carne (halbe Dose)" matches "REWE Beste Wahl Chili Sin Carne"
    for product_name_lower, product_id in lookup.items():
        if name_lower.startswith(product_name_lower):
            return product_id

    # 5. Handle case variations (e.g. "Rewe" vs "REWE")
    for product_name_lower, product_id in lookup.items():
        if name_lower.replace("rewe", "REWE").lower() == product_name_lower:
            return product_id

    return None


def main():
    db = SessionLocal()

    products = db.query(Product).all()
    lookup = build_product_lookup(products)

    ingredients = db.query(Ingredient).all()
    print(f"Matching {len(ingredients)} ingredients to {len(products)} products...\n")

    linked = 0
    unmatched = set()

    for ing in ingredients:
        product_id = find_product_id(ing.product_name, lookup, {})
        if product_id:
            ing.product_id = product_id
            linked += 1
        else:
            unmatched.add(ing.product_name)

    db.commit()

    total = len(ingredients)
    print(f"Linked {linked}/{total} ingredients to products ({linked*100//total}%)")

    if unmatched:
        print(f"\nUnmatched ingredient names ({len(unmatched)}):")
        for name in sorted(unmatched):
            print(f"  - {name}")

    db.close()


if __name__ == "__main__":
    main()
