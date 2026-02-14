"""
Enrich products with EAN barcodes and nutritional data from Open Food Facts API.

Uses the search API to find each product, then updates the database.
Rate limited to 10 requests/minute (7 second delay between requests).

Usage:
    cd backend
    venv/bin/python scripts/enrich_products_off.py
"""

import sys
import os
import time
import json
import urllib.request
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.product import Product

USER_AGENT = "SlothDietApp/1.0 (sloth-diet-app@example.com)"
SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"
FIELDS = "code,product_name,brands,countries_tags,nutriments,nutrition_grades,serving_size"
DELAY = 7  # seconds between requests to respect rate limit


def search_product(name: str, brand: str) -> dict | None:
    """Search Open Food Facts for a product by name and brand."""
    # Build search query combining name and brand
    query = f"{name}"
    if brand and brand not in ("Generic",):
        query = f"{brand} {name}"

    params = {
        "search_terms": query,
        "search_simple": "1",
        "action": "process",
        "json": "1",
        "page_size": "5",
        "fields": FIELDS,
        "tagtype_0": "countries",
        "tag_contains_0": "contains",
        "tag_0": "Germany",
    }

    url = f"{SEARCH_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"    ERROR: {e}")
        return None

    products = data.get("products", [])
    if not products:
        return None

    # Try to find best match - prefer one with nutriments
    for p in products:
        nutriments = p.get("nutriments", {})
        if nutriments.get("energy-kcal_100g") is not None:
            return p

    # Fall back to first result
    return products[0]


def extract_nutrition(off_product: dict) -> dict:
    """Extract nutritional data from OFF product response."""
    n = off_product.get("nutriments", {})
    return {
        "ean": off_product.get("code"),
        "calories_per_100g": n.get("energy-kcal_100g"),
        "protein_per_100g": n.get("proteins_100g"),
        "carbs_per_100g": n.get("carbohydrates_100g"),
        "fat_per_100g": n.get("fat_100g"),
        "fiber_per_100g": n.get("fiber_100g"),
        "sugar_per_100g": n.get("sugars_100g"),
        "salt_per_100g": n.get("salt_100g"),
    }


def main():
    db = SessionLocal()
    products = db.query(Product).order_by(Product.category, Product.name).all()
    print(f"Enriching {len(products)} products from Open Food Facts...\n")

    found = 0
    not_found = []

    for i, product in enumerate(products):
        # Skip generic pantry items (olive oil, butter, vinegar)
        if product.brand == "Generic":
            print(f"[{i+1}/{len(products)}] SKIP (generic): {product.name}")
            not_found.append(product.name)
            continue

        print(f"[{i+1}/{len(products)}] Searching: {product.name} ({product.brand})...", end=" ", flush=True)

        off = search_product(product.name, product.brand)

        if off is None:
            print("NOT FOUND")
            not_found.append(f"{product.name} ({product.brand})")
            time.sleep(DELAY)
            continue

        nutrition = extract_nutrition(off)
        off_name = off.get("product_name", "?")
        ean = nutrition.get("ean", "")
        kcal = nutrition.get("calories_per_100g")

        # Update product
        if ean and len(ean) <= 13:
            product.ean = ean
        if nutrition["calories_per_100g"] is not None:
            product.calories_per_100g = nutrition["calories_per_100g"]
            product.protein_per_100g = nutrition["protein_per_100g"]
            product.carbs_per_100g = nutrition["carbs_per_100g"]
            product.fat_per_100g = nutrition["fat_per_100g"]
            product.fiber_per_100g = nutrition["fiber_per_100g"]
            product.sugar_per_100g = nutrition["sugar_per_100g"]
            product.salt_per_100g = nutrition["salt_per_100g"]
            found += 1
            print(f"OK -> {off_name} (EAN:{ean}, {kcal}kcal)")
        else:
            print(f"FOUND but no nutrition: {off_name}")
            not_found.append(f"{product.name} ({product.brand}) - no nutrition data")

        time.sleep(DELAY)

    db.commit()
    db.close()

    print(f"\n{'='*70}")
    print(f"RESULTS: {found}/{len(products)} products enriched with nutrition data")
    print(f"{'='*70}")

    if not_found:
        print(f"\nNot found / incomplete ({len(not_found)}):")
        for name in not_found:
            print(f"  - {name}")


if __name__ == "__main__":
    main()
