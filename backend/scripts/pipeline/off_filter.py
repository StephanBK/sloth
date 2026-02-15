"""
Filter and transform Open Food Facts data for German products.

Reads the full JSONL dump line-by-line (memory-efficient), filters for German
products with valid nutrition data, transforms to our schema, and outputs
a cleaned JSONL file.

Usage:
    cd backend
    python scripts/pipeline/off_filter.py
"""

import os
import sys
import gzip
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.pipeline.utils import map_off_category, compute_confidence

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
INPUT_FILE = DATA_DIR / "raw" / "openfoodfacts-products.jsonl.gz"
OUTPUT_FILE = DATA_DIR / "processed" / "off_german_products.jsonl"

# Tags that indicate a product is sold in Germany
GERMANY_TAGS = {"en:germany", "de:deutschland", "en:de", "de:germany"}


def is_german_product(raw: dict) -> bool:
    """Check if the product is sold in Germany based on countries_tags."""
    tags = raw.get("countries_tags", [])
    return bool(set(t.lower() for t in tags) & GERMANY_TAGS)


def passes_quality_gate(raw: dict) -> bool:
    """Check minimum data quality requirements."""
    # Must have a product name
    name = raw.get("product_name_de") or raw.get("product_name", "")
    if len(name.strip()) < 2:
        return False

    # Must have a barcode
    code = raw.get("code", "")
    if not code or len(code) < 8:
        return False

    # Must have basic nutrition data
    n = raw.get("nutriments", {})
    kcal = n.get("energy-kcal_100g")
    protein = n.get("proteins_100g")

    if kcal is None or protein is None:
        return False

    # Sanity checks
    try:
        kcal_val = float(kcal)
        protein_val = float(protein)
        if kcal_val < 0 or kcal_val > 9000:
            return False
        if protein_val < 0 or protein_val > 100:
            return False
    except (ValueError, TypeError):
        return False

    # Minimum completeness — keeps only well-documented products
    completeness = raw.get("completeness", 0)
    try:
        if float(completeness) < 0.5:
            return False
    except (ValueError, TypeError):
        return False

    return True


def safe_float(value) -> float | None:
    """Safely convert a value to float, returning None on failure."""
    if value is None:
        return None
    try:
        return round(float(value), 2)
    except (ValueError, TypeError):
        return None


def transform_off_product(raw: dict) -> dict:
    """Transform an OFF raw product to our internal schema."""
    n = raw.get("nutriments", {})
    completeness = raw.get("completeness", 0)
    try:
        completeness = float(completeness)
    except (ValueError, TypeError):
        completeness = 0.0

    name = (raw.get("product_name_de") or raw.get("product_name", "")).strip()
    brands = (raw.get("brands") or "").strip()
    # Take first brand if multiple (comma-separated)
    brand = brands.split(",")[0].strip() if brands else None

    categories_tags = raw.get("categories_tags", [])

    return {
        "name": name,
        "brand": brand,
        "ean": raw.get("code", "").strip(),
        "category": map_off_category(categories_tags),
        "calories_per_100g": safe_float(n.get("energy-kcal_100g")),
        "protein_per_100g": safe_float(n.get("proteins_100g")),
        "carbs_per_100g": safe_float(n.get("carbohydrates_100g")),
        "fat_per_100g": safe_float(n.get("fat_100g")),
        "fiber_per_100g": safe_float(n.get("fiber_100g")),
        "sugar_per_100g": safe_float(n.get("sugars_100g")),
        "salt_per_100g": safe_float(n.get("salt_100g")),
        "nutriscore_grade": raw.get("nutriscore_grade"),
        "image_url": raw.get("image_url"),
        "image_thumb_url": raw.get("image_small_url"),
        "off_id": raw.get("code", "").strip(),
        "completeness": completeness,
        "data_confidence": compute_confidence("off", completeness),
        "stores": raw.get("stores", ""),
    }


def main():
    if not INPUT_FILE.exists():
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        print("Run off_download.py first to download the OFF dump.")
        sys.exit(1)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Reading: {INPUT_FILE}")
    print(f"Writing: {OUTPUT_FILE}")
    print()

    total_scanned = 0
    german_found = 0
    passed_quality = 0
    errors = 0

    try:
        from tqdm import tqdm
        # Estimate ~3M products in the dump
        progress = tqdm(desc="Scanning products", unit=" products")
        use_tqdm = True
    except ImportError:
        use_tqdm = False

    with gzip.open(INPUT_FILE, "rt", encoding="utf-8") as fin, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as fout:

        for line in fin:
            total_scanned += 1

            if use_tqdm and total_scanned % 10000 == 0:
                progress.update(10000)
                progress.set_postfix(
                    german=german_found,
                    quality=passed_quality,
                )
            elif not use_tqdm and total_scanned % 100000 == 0:
                print(f"  Scanned {total_scanned:,} | German: {german_found:,} | Quality: {passed_quality:,}")

            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                errors += 1
                continue

            if not is_german_product(raw):
                continue
            german_found += 1

            if not passes_quality_gate(raw):
                continue

            transformed = transform_off_product(raw)

            # Skip categories not relevant for a diet app (candy, soda, alcohol, etc.)
            if transformed["category"] in ("SKIP", "Other"):
                continue

            fout.write(json.dumps(transformed, ensure_ascii=False) + "\n")
            passed_quality += 1

    if use_tqdm:
        progress.update(total_scanned % 10000)
        progress.close()

    print(f"\n{'='*60}")
    print(f"OFF Filter Results")
    print(f"{'='*60}")
    print(f"Total scanned:       {total_scanned:,}")
    print(f"German products:     {german_found:,}")
    print(f"Passed quality gate: {passed_quality:,}")
    print(f"JSON parse errors:   {errors:,}")
    print(f"Output file:         {OUTPUT_FILE}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
