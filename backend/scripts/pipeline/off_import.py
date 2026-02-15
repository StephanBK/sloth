"""
Fast bulk import of filtered Open Food Facts products into the database.

Reads the filtered JSONL file, deduplicates by EAN (fast dict lookup),
and bulk inserts new products in large batches.

Usage:
    cd backend
    python scripts/pipeline/off_import.py [--dry-run]
"""

import os
import sys
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal
from app.models.product import Product

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
INPUT_FILE = DATA_DIR / "processed" / "off_german_products.jsonl"

BATCH_SIZE = 5000  # Large batches for speed


def main():
    dry_run = "--dry-run" in sys.argv

    if not INPUT_FILE.exists():
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        print("Run off_filter.py first to create the filtered JSONL file.")
        sys.exit(1)

    if dry_run:
        print("*** DRY RUN MODE - no database changes will be made ***\n")

    db = SessionLocal()

    # Build EAN index from existing products (fast dict lookup)
    print("Loading existing products...")
    existing = db.query(Product.ean).filter(Product.ean.isnot(None)).all()
    existing_eans = {row[0] for row in existing}
    print(f"  {len(existing_eans)} existing EANs in database\n")

    # First pass: deduplicate the JSONL file by EAN (keep highest completeness)
    print("Pass 1: Deduplicating by EAN...")
    best_by_ean = {}   # ean -> item dict
    no_ean_items = []   # items without EAN (skip these)
    total_lines = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            total_lines += 1
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue

            ean = item.get("ean", "").strip()
            name = item.get("name", "").strip()

            if not name:
                continue

            if not ean:
                # Skip products without barcode — too hard to deduplicate
                continue

            # Skip if already in our database
            if ean in existing_eans:
                continue

            # Keep the one with highest completeness per EAN
            existing_item = best_by_ean.get(ean)
            if existing_item is None or item.get("completeness", 0) > existing_item.get("completeness", 0):
                best_by_ean[ean] = item

    unique_products = list(best_by_ean.values())
    print(f"  Total lines: {total_lines:,}")
    print(f"  Unique new products (by EAN): {len(unique_products):,}")
    print(f"  Skipped (already in DB): {total_lines - len(unique_products) - len(no_ean_items):,}\n")

    if dry_run:
        print(f"DRY RUN complete. Would insert {len(unique_products):,} products.")
        db.close()
        return

    # Second pass: bulk insert in batches
    print(f"Pass 2: Inserting {len(unique_products):,} products in batches of {BATCH_SIZE}...")
    now = datetime.now(timezone.utc)
    inserted = 0

    for i in range(0, len(unique_products), BATCH_SIZE):
        batch = unique_products[i:i + BATCH_SIZE]
        new_products = []

        for item in batch:
            product = Product(
                id=str(uuid.uuid4()),
                name=item["name"][:255],
                brand=(item.get("brand") or "")[:255] or None,
                ean=item.get("ean")[:13] if item.get("ean") and len(item.get("ean")) <= 13 else None,
                category=item.get("category", "Other"),
                package_size=None,
                unit=None,
                calories_per_100g=item.get("calories_per_100g"),
                protein_per_100g=item.get("protein_per_100g"),
                carbs_per_100g=item.get("carbs_per_100g"),
                fat_per_100g=item.get("fat_per_100g"),
                fiber_per_100g=item.get("fiber_per_100g"),
                sugar_per_100g=item.get("sugar_per_100g"),
                salt_per_100g=item.get("salt_per_100g"),
                data_source="off",
                data_confidence=item.get("data_confidence", 0.3),
                is_curated=False,
                off_id=item.get("off_id"),
                nutriscore_grade=item.get("nutriscore_grade") if item.get("nutriscore_grade") in ("a","b","c","d","e") else None,
                image_url=item.get("image_url"),
                image_thumb_url=item.get("image_thumb_url"),
                last_synced_at=now,
            )
            new_products.append(product)

        db.bulk_save_objects(new_products)
        db.commit()
        inserted += len(new_products)
        print(f"  Inserted {inserted:,} / {len(unique_products):,}")

    db.close()

    print(f"\n{'='*60}")
    print(f"OFF Import Results")
    print(f"{'='*60}")
    print(f"Total lines read:    {total_lines:,}")
    print(f"New products added:  {inserted:,}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
