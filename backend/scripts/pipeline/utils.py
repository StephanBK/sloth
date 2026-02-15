"""
Shared utilities for the data pipeline.

Provides normalization, fuzzy matching, category mapping, and confidence scoring
used across all pipeline scripts (OFF, BLS, dedup).
"""

import re
from difflib import SequenceMatcher


# ---------------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------------

def normalize_for_matching(name: str, brand: str = "") -> str:
    """Normalize product name + brand for fuzzy matching.

    Lowercases, strips size indicators (500g, 1L), removes punctuation,
    and collapses whitespace.
    """
    text = f"{brand} {name}".lower().strip() if brand else name.lower().strip()
    # Remove size/weight indicators
    text = re.sub(r'\d+\s*(g|ml|kg|l|cl|dl)\b', '', text)
    # Remove common noise characters
    text = re.sub(r'[®™©,.\-–—/()!?"\']', ' ', text)
    # Collapse whitespace
    return ' '.join(text.split())


def fuzzy_match(candidate: str, existing_index: dict[str, str], threshold: float = 0.85) -> tuple[str | None, float]:
    """Find the best fuzzy match for a candidate string in an index.

    Args:
        candidate: Normalized string to match.
        existing_index: Dict mapping normalized_key -> product_id.
        threshold: Minimum similarity ratio (0-1).

    Returns:
        Tuple of (product_id or None, best_ratio).
    """
    best_ratio = 0.0
    best_id = None
    for existing_key, product_id in existing_index.items():
        ratio = SequenceMatcher(None, candidate, existing_key).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_id = product_id
    return (best_id, best_ratio) if best_ratio >= threshold else (None, best_ratio)


# ---------------------------------------------------------------------------
# OFF category mapping
# ---------------------------------------------------------------------------

# Maps Open Food Facts categories_tags to our internal categories.
# OFF tags look like "en:dairy", "en:meats", etc.
_OFF_CATEGORY_MAP = {
    # Dairy & Eggs
    "en:dairies": "Dairy & Eggs",
    "en:dairy": "Dairy & Eggs",
    "en:milks": "Dairy & Eggs",
    "en:yogurts": "Dairy & Eggs",
    "en:cheeses": "Dairy & Eggs",
    "en:eggs": "Dairy & Eggs",
    "en:butters": "Dairy & Eggs",
    "en:creams": "Dairy & Eggs",
    "en:quark": "Dairy & Eggs",
    "en:fermented-milk-products": "Dairy & Eggs",

    # Protein - Meat & Fish
    "en:meats": "Protein - Meat & Fish",
    "en:poultry": "Protein - Meat & Fish",
    "en:fishes": "Protein - Meat & Fish",
    "en:seafood": "Protein - Meat & Fish",
    "en:smoked-fishes": "Protein - Meat & Fish",
    "en:sausages": "Protein - Meat & Fish",
    "en:hams": "Protein - Meat & Fish",
    "en:beef": "Protein - Meat & Fish",
    "en:pork": "Protein - Meat & Fish",
    "en:chicken": "Protein - Meat & Fish",

    # Protein - Plant-based
    "en:meat-alternatives": "Protein - Plant-based",
    "en:tofu": "Protein - Plant-based",
    "en:tempeh": "Protein - Plant-based",
    "en:seitan": "Protein - Plant-based",

    # Grains & Cereals
    "en:cereals-and-potatoes": "Grains & Cereals",
    "en:cereals": "Grains & Cereals",
    "en:breads": "Grains & Cereals",
    "en:pastas": "Grains & Cereals",
    "en:rices": "Grains & Cereals",
    "en:breakfast-cereals": "Grains & Cereals",
    "en:flours": "Grains & Cereals",
    "en:oats": "Grains & Cereals",
    "en:noodles": "Grains & Cereals",
    "en:potatoes": "Grains & Cereals",

    # Vegetables & Frozen Veg
    "en:vegetables": "Vegetables & Frozen Veg",
    "en:frozen-vegetables": "Vegetables & Frozen Veg",
    "en:canned-vegetables": "Vegetables & Frozen Veg",
    "en:salads": "Vegetables & Frozen Veg",
    "en:legumes": "Vegetables & Frozen Veg",

    # Frozen Meals
    "en:frozen-foods": "Frozen Meals",
    "en:frozen-meals": "Frozen Meals",
    "en:prepared-meals": "Frozen Meals",

    # Canned & Shelf-stable
    "en:canned-foods": "Canned & Shelf-stable",
    "en:canned-fruits": "Canned & Shelf-stable",
    "en:soups": "Canned & Shelf-stable",
    "en:sauces": "Canned & Shelf-stable",
    "en:condiments": "Canned & Shelf-stable",

    # Fruit (healthy items only — snacks/candy excluded below)
    "en:fruits": "Fruit & Snacks",
    "en:dried-fruits": "Fruit & Snacks",
    "en:nuts": "Fruit & Snacks",
    "en:fruit-juices": "Fruit & Snacks",

    # Pantry
    "en:oils-and-fats": "Pantry",
    "en:olive-oils": "Pantry",
    "en:vinegars": "Pantry",
    "en:spices": "Pantry",
    "en:honey": "Pantry",

    # --- SKIP: not relevant for a diet app ---
    "en:snacks": "SKIP",
    "en:chocolates": "SKIP",
    "en:biscuits": "SKIP",
    "en:candies": "SKIP",
    "en:confectioneries": "SKIP",
    "en:sweeteners": "SKIP",
    "en:cakes": "SKIP",
    "en:pastries": "SKIP",
    "en:ice-creams": "SKIP",
    "en:chips": "SKIP",
    "en:crackers": "SKIP",
    "en:sweets": "SKIP",
    "en:sodas": "SKIP",
    "en:alcoholic-beverages": "SKIP",
    "en:beers": "SKIP",
    "en:wines": "SKIP",
    "en:spirits": "SKIP",
    "en:energy-drinks": "SKIP",
    "en:beverages": "SKIP",
    "en:waters": "SKIP",
    "en:pizzas": "SKIP",
}


def map_off_category(categories_tags: list[str]) -> str:
    """Map Open Food Facts categories_tags to our internal category.

    Iterates through the product's tags and returns the first match.
    Falls back to "Other" if no match is found.
    """
    for tag in categories_tags:
        tag_lower = tag.lower()
        if tag_lower in _OFF_CATEGORY_MAP:
            return _OFF_CATEGORY_MAP[tag_lower]
    return "Other"


# ---------------------------------------------------------------------------
# BLS category mapping
# ---------------------------------------------------------------------------

# BLS food group codes (first letter of the BLS code)
_BLS_CATEGORY_MAP = {
    "B": "Grains & Cereals",      # Brot (Bread)
    "C": "Grains & Cereals",      # Cerealien (Cereals)
    "D": "Other",                  # Diverse (Miscellaneous)
    "E": "Dairy & Eggs",          # Eier (Eggs)
    "F": "Fruit & Snacks",        # Früchte (Fruits)
    "G": "Vegetables & Frozen Veg",  # Gemüse (Vegetables)
    "H": "Vegetables & Frozen Veg",  # Hülsenfrüchte (Legumes)
    "K": "Grains & Cereals",      # Kartoffeln (Potatoes)
    "M": "Dairy & Eggs",          # Milch (Dairy)
    "N": "Grains & Cereals",      # Nudeln (Pasta)
    "O": "Fruit & Snacks",        # Obst (same as Früchte)
    "P": "Protein - Meat & Fish", # (reserved)
    "Q": "Other",                 # (reserved)
    "R": "Protein - Meat & Fish", # Rind (Beef)
    "S": "Pantry",                # Speisefette (Fats/Oils)
    "T": "Protein - Meat & Fish", # Fleisch (Meat general)
    "U": "Protein - Meat & Fish", # Fisch (Fish)
    "V": "Protein - Meat & Fish", # Geflügel (Poultry)
    "W": "Protein - Meat & Fish", # Wurst (Sausages)
    "X": "Other",                 # Süßwaren (Sweets)
    "Y": "Other",                 # Getränke (Beverages)
    "Z": "Pantry",                # Zucker/Gewürze (Sugar/Spices)
}


def map_bls_category(bls_code: str) -> str:
    """Map a BLS food code to our internal category.

    BLS codes start with a letter indicating the food group.
    """
    if not bls_code:
        return "Other"
    first_char = bls_code[0].upper()
    return _BLS_CATEGORY_MAP.get(first_char, "Other")


# ---------------------------------------------------------------------------
# Data confidence scoring
# ---------------------------------------------------------------------------

def compute_confidence(data_source: str, completeness: float = 0.0) -> float:
    """Compute a data confidence score (0.0-1.0) for a product.

    Args:
        data_source: "manual", "off", "bls"
        completeness: OFF completeness score (0-1), ignored for other sources.
    """
    if data_source == "manual":
        return 1.0
    elif data_source == "bls":
        return 0.95
    elif data_source == "off":
        if completeness >= 0.8:
            return 0.8
        elif completeness >= 0.5:
            return 0.5
        else:
            return 0.3
    return 0.3
