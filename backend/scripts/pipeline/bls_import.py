"""
Import BLS 4.0 (Bundeslebensmittelschlüssel) data into the product catalog.

The BLS is a scientific food composition database from the Max Rubner-Institut.
It provides ~7,140 generic food items with 138 nutritional values — perfect for
fresh/unbranded items like fruits, vegetables, and raw ingredients.

Prerequisites:
    1. Download BLS 4.0 from: https://www.openagrar.de/receive/openagrar_mods_00112643
       (or search "Bundeslebensmittelschlüssel 4.0" on openagrar.de)
    2. Place the Excel/CSV file(s) in: data/raw/bls/
    3. Adjust COLUMN_MAP below if the column names differ from expected

Usage:
    cd backend
    python scripts/pipeline/bls_import.py [--dry-run]
"""

import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal
from app.models.product import Product
from scripts.pipeline.utils import normalize_for_matching, fuzzy_match, map_bls_category

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "raw" / "bls"

# Expected column names in the BLS file. Adjust these if the actual file differs.
# The BLS file may use German column names — update this mapping accordingly.
COLUMN_MAP = {
    "code": "SBLS",           # BLS food code
    "name_de": "ST",          # German food name (Stichwort)
    "name_en": "STE",         # English name (if available)
    "energy_kcal": "GCAL",    # Energy in kcal
    "protein": "ZE",          # Protein in g
    "fat": "ZF",              # Fat in g
    "carbs": "ZK",            # Carbohydrates in g
    "fiber": "ZB",            # Dietary fiber in g
    "sugar": "ZZ",            # Sugar in g
    "sodium": "NA",           # Sodium in mg (multiply by 2.5/1000 for salt in g)
}


def find_bls_file() -> Path | None:
    """Look for the BLS data file in the expected directory."""
    if not DATA_DIR.exists():
        return None

    # Try common file patterns
    for pattern in ["*.xlsx", "*.xls", "*.csv", "*.tsv"]:
        files = list(DATA_DIR.glob(pattern))
        if files:
            return files[0]

    return None


def load_bls_data(filepath: Path) -> list[dict]:
    """Load and parse the BLS data file.

    Returns a list of dicts with standardized keys.
    """
    suffix = filepath.suffix.lower()

    if suffix in (".xlsx", ".xls"):
        try:
            import openpyxl
        except ImportError:
            print("ERROR: openpyxl is required. Install it: pip install openpyxl")
            sys.exit(1)

        import pandas as pd
        df = pd.read_excel(filepath, engine="openpyxl")
    elif suffix == ".csv":
        import pandas as pd
        df = pd.read_csv(filepath, encoding="utf-8")
    elif suffix == ".tsv":
        import pandas as pd
        df = pd.read_csv(filepath, sep="\t", encoding="utf-8")
    else:
        print(f"ERROR: Unsupported file format: {suffix}")
        sys.exit(1)

    print(f"Loaded {len(df)} rows from {filepath.name}")
    print(f"Columns found: {list(df.columns)}")

    # Try to detect column mapping
    col_map = {}
    available_cols = set(df.columns)

    for our_key, expected_col in COLUMN_MAP.items():
        if expected_col in available_cols:
            col_map[our_key] = expected_col
        else:
            # Try case-insensitive match
            for col in available_cols:
                if col.lower() == expected_col.lower():
                    col_map[our_key] = col
                    break

    # Check for required columns
    required = ["code", "name_de", "energy_kcal", "protein"]
    missing = [k for k in required if k not in col_map]
    if missing:
        print(f"\nERROR: Could not find required columns: {missing}")
        print(f"Expected column names (adjust COLUMN_MAP in script):")
        for k, v in COLUMN_MAP.items():
            status = "FOUND" if k in col_map else "MISSING"
            print(f"  {k:15s} -> {v:10s} [{status}]")
        print(f"\nAvailable columns in file: {sorted(available_cols)}")
        sys.exit(1)

    print(f"Column mapping: {col_map}")

    items = []
    for _, row in df.iterrows():
        code = str(row.get(col_map["code"], "")).strip()
        name = str(row.get(col_map["name_de"], "")).strip()

        if not code or not name or name == "nan":
            continue

        def safe_float(key):
            if key not in col_map:
                return None
            val = row.get(col_map[key])
            try:
                return round(float(val), 2)
            except (ValueError, TypeError):
                return None

        # Convert sodium (mg) to salt (g): salt = sodium * 2.5 / 1000
        sodium = safe_float("sodium")
        salt = round(sodium * 2.5 / 1000, 2) if sodium is not None else None

        items.append({
            "bls_code": code,
            "name": name,
            "energy_kcal": safe_float("energy_kcal"),
            "protein": safe_float("protein"),
            "fat": safe_float("fat"),
            "carbs": safe_float("carbs"),
            "fiber": safe_float("fiber"),
            "sugar": safe_float("sugar"),
            "salt": salt,
        })

    return items


def filter_raw_items(items: list[dict]) -> list[dict]:
    """Filter for raw/unprocessed food items.

    BLS codes often encode preparation state. We prefer raw items
    to avoid duplicates (e.g., "Banane, roh" vs "Banane, gebacken").
    """
    filtered = []
    for item in items:
        name_lower = item["name"].lower()
        # Skip items with preparation indicators (unless it's the only version)
        # Common German preparation terms to exclude
        skip_terms = [
            "gegart", "gebraten", "gekocht", "gebacken", "frittiert",
            "gedünstet", "gegrillt", "geschmort", "blanchiert",
            "tiefgefroren", "konserve", "dose",
        ]
        if any(term in name_lower for term in skip_terms):
            continue

        # Must have at least energy + protein
        if item.get("energy_kcal") is None or item.get("protein") is None:
            continue

        filtered.append(item)

    return filtered


def main():
    dry_run = "--dry-run" in sys.argv

    bls_file = find_bls_file()
    if bls_file is None:
        print("ERROR: No BLS data file found.")
        print(f"\nExpected location: {DATA_DIR}/")
        print("\nTo get the BLS 4.0 data:")
        print("  1. Visit: https://www.openagrar.de/receive/openagrar_mods_00112643")
        print("  2. Download the Excel/CSV file")
        print(f"  3. Place it in: {DATA_DIR}/")
        print("  4. Re-run this script")
        sys.exit(1)

    if dry_run:
        print("*** DRY RUN MODE ***\n")

    print(f"BLS file: {bls_file}\n")

    # Load and parse
    items = load_bls_data(bls_file)
    print(f"\nTotal BLS items parsed: {len(items):,}")

    # Filter for raw items
    filtered = filter_raw_items(items)
    print(f"After filtering (raw only): {len(filtered):,}")

    # Build dedup index from existing products
    db = SessionLocal()
    existing_products = db.query(Product).all()
    name_index = {}
    for p in existing_products:
        key = normalize_for_matching(p.name, p.brand or "")
        if key:
            name_index[key] = p.id
    print(f"Existing products for dedup: {len(name_index)}")

    # Import
    inserted = 0
    skipped_dup = 0
    skipped_other = 0

    for item in filtered:
        candidate = normalize_for_matching(item["name"])
        matched_id, ratio = fuzzy_match(candidate, name_index, threshold=0.80)

        if matched_id:
            skipped_dup += 1
            continue

        category = map_bls_category(item["bls_code"])

        product = Product(
            id=str(uuid.uuid4()),
            name=item["name"],
            brand=None,
            ean=None,
            category=category,
            package_size=None,
            unit=None,
            calories_per_100g=item["energy_kcal"],
            protein_per_100g=item["protein"],
            carbs_per_100g=item["carbs"],
            fat_per_100g=item["fat"],
            fiber_per_100g=item["fiber"],
            sugar_per_100g=item["sugar"],
            salt_per_100g=item["salt"],
            data_source="bls",
            data_confidence=0.95,
            is_curated=False,
            bls_code=item["bls_code"],
            last_synced_at=datetime.utcnow(),
        )

        if not dry_run:
            db.add(product)

        # Update index for subsequent dedup
        if candidate:
            name_index[candidate] = product.id

        inserted += 1

    if not dry_run:
        db.commit()

    db.close()

    print(f"\n{'='*60}")
    print(f"BLS Import Results {'(DRY RUN)' if dry_run else ''}")
    print(f"{'='*60}")
    print(f"Total parsed:        {len(items):,}")
    print(f"Filtered (raw only): {len(filtered):,}")
    print(f"Skipped (duplicate): {skipped_dup:,}")
    print(f"Inserted:            {inserted:,}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
