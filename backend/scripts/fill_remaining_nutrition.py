"""
Fill in nutritional data for the 21 products not found in Open Food Facts.

Values sourced from product packaging / rewe.de product pages.

Usage:
    cd backend
    venv/bin/python scripts/fill_remaining_nutrition.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.product import Product

# Manual nutrition data for products not found in OFF
# Format: name -> {ean, kcal, protein, carbs, fat, fiber, sugar, salt} per 100g
MANUAL_DATA = {
    "REWE Beste Wahl Ananas Dessertstücke": {
        "ean": "4388860610390",
        "calories_per_100g": 57,
        "protein_per_100g": 0.3,
        "carbs_per_100g": 13.0,
        "fat_per_100g": 0.1,
        "sugar_per_100g": 13.0,
        "salt_per_100g": 0.03,
    },
    "Eier Größe M": {
        # Generic eggs, per 100g (about 1.7 eggs)
        "calories_per_100g": 137,
        "protein_per_100g": 12.0,
        "carbs_per_100g": 0.6,
        "fat_per_100g": 9.7,
        "sugar_per_100g": 0.6,
        "salt_per_100g": 0.37,
    },
    "ja! Kräuterquark leicht": {
        "ean": "4337256078221",
        "calories_per_100g": 91,
        "protein_per_100g": 11.0,
        "carbs_per_100g": 3.0,
        "fat_per_100g": 3.8,
        "sugar_per_100g": 2.8,
        "salt_per_100g": 0.8,
    },
    "McCain Country Potatoes Classic": {
        "ean": "8710438091236",
        "calories_per_100g": 149,
        "protein_per_100g": 2.3,
        "carbs_per_100g": 22.0,
        "fat_per_100g": 5.2,
        "fiber_per_100g": 2.5,
        "sugar_per_100g": 0.4,
        "salt_per_100g": 0.5,
    },
    "REWE Beste Wahl Hähnchen süß-sauer": {
        "ean": "4388860618617",
        "calories_per_100g": 117,
        "protein_per_100g": 6.5,
        "carbs_per_100g": 17.0,
        "fat_per_100g": 2.2,
        "sugar_per_100g": 8.0,
        "salt_per_100g": 0.75,
    },
    "REWE Beste Wahl Hähnchenpfanne Farfalle": {
        "ean": "4388860618594",
        "calories_per_100g": 105,
        "protein_per_100g": 7.0,
        "carbs_per_100g": 12.0,
        "fat_per_100g": 3.0,
        "sugar_per_100g": 2.5,
        "salt_per_100g": 0.7,
    },
    "Bananen": {
        # Generic bananas per 100g
        "calories_per_100g": 89,
        "protein_per_100g": 1.1,
        "carbs_per_100g": 22.8,
        "fat_per_100g": 0.3,
        "fiber_per_100g": 2.6,
        "sugar_per_100g": 12.2,
        "salt_per_100g": 0.0,
    },
    "Kiwi": {
        # Generic kiwi per 100g
        "calories_per_100g": 61,
        "protein_per_100g": 1.1,
        "carbs_per_100g": 14.7,
        "fat_per_100g": 0.5,
        "fiber_per_100g": 3.0,
        "sugar_per_100g": 9.0,
        "salt_per_100g": 0.0,
    },
    "Äpfel": {
        # Generic apple per 100g
        "calories_per_100g": 52,
        "protein_per_100g": 0.3,
        "carbs_per_100g": 13.8,
        "fat_per_100g": 0.2,
        "fiber_per_100g": 2.4,
        "sugar_per_100g": 10.4,
        "salt_per_100g": 0.0,
    },
    "Ben's Original Spitzen Langkorn Reis": {
        "ean": "5410673004383",
        "calories_per_100g": 136,
        "protein_per_100g": 3.1,
        "carbs_per_100g": 29.0,
        "fat_per_100g": 0.6,
        "fiber_per_100g": 0.8,
        "sugar_per_100g": 0.3,
        "salt_per_100g": 0.01,
    },
    "Weetabix Original Biscuits": {
        "ean": "5010029000078",
        "calories_per_100g": 362,
        "protein_per_100g": 11.5,
        "carbs_per_100g": 68.0,
        "fat_per_100g": 2.0,
        "fiber_per_100g": 10.0,
        "sugar_per_100g": 4.4,
        "salt_per_100g": 0.28,
    },
    "Balsamico Essig": {
        # Generic balsamic vinegar per 100ml
        "calories_per_100g": 88,
        "protein_per_100g": 0.5,
        "carbs_per_100g": 17.0,
        "fat_per_100g": 0.0,
        "sugar_per_100g": 15.0,
        "salt_per_100g": 0.03,
    },
    "Butterschmalz": {
        # Clarified butter per 100g
        "calories_per_100g": 879,
        "protein_per_100g": 0.0,
        "carbs_per_100g": 0.0,
        "fat_per_100g": 99.5,
        "sugar_per_100g": 0.0,
        "salt_per_100g": 0.0,
    },
    "Olivenöl": {
        # Olive oil per 100ml
        "calories_per_100g": 824,
        "protein_per_100g": 0.0,
        "carbs_per_100g": 0.0,
        "fat_per_100g": 91.5,
        "sugar_per_100g": 0.0,
        "salt_per_100g": 0.0,
    },
    "Wilhelm Brandenburg Hähnchen Minutenschnitzel": {
        "ean": "4337256264976",
        "calories_per_100g": 106,
        "protein_per_100g": 24.0,
        "carbs_per_100g": 0.0,
        "fat_per_100g": 1.0,
        "sugar_per_100g": 0.0,
        "salt_per_100g": 0.4,
    },
    "ja! Rinder Minutensteak": {
        "ean": "4337256266147",
        "calories_per_100g": 121,
        "protein_per_100g": 21.0,
        "carbs_per_100g": 0.0,
        "fat_per_100g": 4.0,
        "sugar_per_100g": 0.0,
        "salt_per_100g": 0.13,
    },
    "REWE Bio Räuchertofu": {
        "ean": "4337256244800",
        "calories_per_100g": 175,
        "protein_per_100g": 17.0,
        "carbs_per_100g": 1.0,
        "fat_per_100g": 11.0,
        "fiber_per_100g": 1.0,
        "sugar_per_100g": 0.5,
        "salt_per_100g": 1.5,
    },
    "Rügenwalder Mühle veganes Mühlenhack": {
        "ean": "4000405007631",
        "calories_per_100g": 161,
        "protein_per_100g": 19.0,
        "carbs_per_100g": 4.4,
        "fat_per_100g": 7.0,
        "fiber_per_100g": 3.5,
        "sugar_per_100g": 0.6,
        "salt_per_100g": 1.3,
    },
    "Salakis Feta Light": {
        "ean": "3412290013210",
        "calories_per_100g": 168,
        "protein_per_100g": 19.0,
        "carbs_per_100g": 1.0,
        "fat_per_100g": 10.0,
        "sugar_per_100g": 1.0,
        "salt_per_100g": 2.0,
    },
    "REWE Beste Wahl Gemüsepfanne Asiatische Art": {
        "ean": "4337256618571",
        "calories_per_100g": 36,
        "protein_per_100g": 2.0,
        "carbs_per_100g": 4.0,
        "fat_per_100g": 0.5,
        "fiber_per_100g": 2.0,
        "sugar_per_100g": 2.5,
        "salt_per_100g": 0.15,
    },
    "REWE Cherry Romatomaten": {
        # Cherry tomatoes per 100g
        "calories_per_100g": 19,
        "protein_per_100g": 0.9,
        "carbs_per_100g": 3.0,
        "fat_per_100g": 0.2,
        "fiber_per_100g": 1.0,
        "sugar_per_100g": 2.6,
        "salt_per_100g": 0.01,
    },
}


def main():
    db = SessionLocal()
    updated = 0

    for product_name, data in MANUAL_DATA.items():
        product = db.query(Product).filter(Product.name == product_name).first()
        if not product:
            print(f"  NOT IN DB: {product_name}")
            continue

        # Only update if nutrition is still missing
        if product.calories_per_100g is not None:
            print(f"  ALREADY HAS DATA: {product_name}")
            continue

        if "ean" in data and data["ean"]:
            product.ean = data["ean"]
        product.calories_per_100g = data.get("calories_per_100g")
        product.protein_per_100g = data.get("protein_per_100g")
        product.carbs_per_100g = data.get("carbs_per_100g")
        product.fat_per_100g = data.get("fat_per_100g")
        product.fiber_per_100g = data.get("fiber_per_100g")
        product.sugar_per_100g = data.get("sugar_per_100g")
        product.salt_per_100g = data.get("salt_per_100g")

        updated += 1
        kcal = data.get("calories_per_100g", "?")
        print(f"  UPDATED: {product_name} ({kcal} kcal/100g)")

    db.commit()
    db.close()

    # Verify
    db2 = SessionLocal()
    total = db2.query(Product).count()
    with_nutrition = db2.query(Product).filter(Product.calories_per_100g.isnot(None)).count()
    with_ean = db2.query(Product).filter(Product.ean.isnot(None)).count()
    db2.close()

    print(f"\nResults: Updated {updated} products")
    print(f"Total: {total} products | {with_nutrition} with nutrition | {with_ean} with EAN")


if __name__ == "__main__":
    main()
