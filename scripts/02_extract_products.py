#!/usr/bin/env python3
"""
Script: Extract Unique Products from Sloth Diet Meal Plans

This script analyzes the Männer Pläne document and extracts all unique products
to create our master product database.

Learning Points:
- Text parsing and pattern matching
- Data cleaning and normalization
- Creating structured data from unstructured text
- Set operations (finding unique items)

Author: Stephan & Claude
Date: 2025-02-14
"""

import re
from collections import defaultdict
from docx import Document

# ==============================================================================
# CONFIGURATION
# ==============================================================================

INPUT_FILE = "/mnt/user-data/uploads/Ma_nner_Pla_ne.docx"
OUTPUT_FILE = "/home/claude/sloth/data/processed/unique_products.txt"

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def extract_products_from_text(text):
    """
    Extract product mentions from meal plan text.
    
    This is tricky because products are described in different ways:
    - "500g ja! Skyr natur"
    - "2x200g REWE Beste Wahl High Protein Quarkcreme"
    - "1 EL Olivenöl"
    - "6 Eier Größe M"
    
    Args:
        text (str): Raw text from the document
        
    Returns:
        list: List of product strings found
    """
    products = []
    
    # Split text into lines
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Skip lines that are clearly headers or totals
        if any(keyword in line.lower() for keyword in ['level', 'tag', 'gesamt:', 'kcal', 'p kh f']):
            continue
            
        # Skip pure macro numbers (like "52g 34g 4g 422")
        if re.match(r'^\d+g?\s+\d+g?\s+\d+g?\s+\d+$', line):
            continue
            
        # This line probably contains a product if it has:
        # - A quantity (number + g/ml/x or words like "Eier", "EL")
        # - A product name (brand or food item)
        
        # Pattern: starts with quantity
        if re.match(r'^\d+\.?\d*\s*(g|ml|x|kg|EL|Eier|Banane|Apfel|Kiwi)', line, re.IGNORECASE):
            products.append(line)
            
    return products

def categorize_product(product_text):
    """
    Try to categorize a product based on keywords.
    
    Categories:
    - Dairy (Quark, Skyr, Milch, Käse)
    - Protein (Hähnchen, Rind, Lachs, Tofu, Hack)
    - Vegetables (Broccoli, Tomaten, Gemüse)
    - Grains (Reis, Porridge, Waffeln)
    - Frozen (Frosta, McCain, Iglo)
    - Snacks (Mandeln, Obst)
    - Pantry (Öl, Essig)
    
    Args:
        product_text (str): Product description
        
    Returns:
        str: Category name
    """
    text_lower = product_text.lower()
    
    if any(word in text_lower for word in ['quark', 'skyr', 'pudding', 'shake', 'eier']):
        return 'Dairy & Eggs'
    elif any(word in text_lower for word in ['hähnchen', 'chicken', 'rind', 'lachs', 'hack', 'tofu', 'gyros', 'steak']):
        return 'Protein'
    elif any(word in text_lower for word in ['broccoli', 'tomaten', 'gemüse', 'kaisergemüse', 'wok mix']):
        return 'Vegetables & Frozen'
    elif any(word in text_lower for word in ['reis', 'porridge', 'waffeln', 'weetabix']):
        return 'Grains & Cereals'
    elif any(word in text_lower for word in ['frosta', 'mccain', 'iglo', 'bohnen', 'ananas']):
        return 'Frozen & Canned'
    elif any(word in text_lower for word in ['mandeln', 'apfel', 'banane', 'kiwi', 'himbeer', 'heidelbeer']):
        return 'Snacks & Fruit'
    elif any(word in text_lower for word in ['olivenöl', 'butterschmalz', 'essig', 'balsamico']):
        return 'Pantry'
    else:
        return 'Other'

def clean_product_name(product_text):
    """
    Clean up product text to extract just the product name.
    
    Example:
    "2x200g REWE Beste Wahl High Protein Quarkcreme (Geschmack egal)"
    → "REWE Beste Wahl High Protein Quarkcreme"
    
    Args:
        product_text (str): Raw product description
        
    Returns:
        str: Cleaned product name
    """
    # Remove quantity at the beginning (e.g., "500g ", "2x200g ", "6 ")
    cleaned = re.sub(r'^\d+\.?\d*\s*x?\s*\d*\.?\d*\s*(g|ml|kg|L)?\s*', '', product_text, flags=re.IGNORECASE)
    
    # Remove notes in parentheses
    cleaned = re.sub(r'\([^)]*\)', '', cleaned)
    
    # Remove preparation notes
    cleaned = re.sub(r'\d+\s*EL\s+.*', '', cleaned)
    
    # Clean up whitespace
    cleaned = ' '.join(cleaned.split())
    
    return cleaned.strip()

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("PRODUCT EXTRACTOR - Sloth Diet Meal Plans")
    print("="*70)
    print()
    
    print(f"📖 Reading document: {INPUT_FILE}")
    
    # Read the Word document
    doc = Document(INPUT_FILE)
    
    # Extract all text
    full_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    
    print(f"✅ Document loaded ({len(full_text)} characters)")
    print()
    
    # Extract products
    print("🔍 Extracting products...")
    all_products = extract_products_from_text(full_text)
    
    print(f"📊 Found {len(all_products)} product mentions")
    print()
    
    # Get unique products (clean and deduplicate)
    unique_products = {}  # Dictionary: cleaned_name → original_texts
    
    for product in all_products:
        cleaned = clean_product_name(product)
        
        if cleaned:  # Only if we got a valid product name
            if cleaned not in unique_products:
                unique_products[cleaned] = []
            unique_products[cleaned].append(product)
    
    print(f"✨ Found {len(unique_products)} unique products")
    print()
    
    # Categorize products
    categorized = defaultdict(list)
    
    for product_name in sorted(unique_products.keys()):
        category = categorize_product(product_name)
        categorized[category].append(product_name)
    
    # Display results
    print("="*70)
    print("UNIQUE PRODUCTS BY CATEGORY")
    print("="*70)
    print()
    
    for category in sorted(categorized.keys()):
        print(f"\n📦 {category}:")
        print("-" * 50)
        for product in sorted(categorized[category]):
            # Show how many times this product appeared
            count = len(unique_products[product])
            print(f"  • {product} (appears {count}x)")
    
    print()
    print("="*70)
    
    # Save to file
    print(f"\n💾 Saving to: {OUTPUT_FILE}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("SLOTH DIET - UNIQUE PRODUCTS\n")
        f.write("="*70 + "\n\n")
        
        for category in sorted(categorized.keys()):
            f.write(f"\n{category}:\n")
            f.write("-" * 50 + "\n")
            for product in sorted(categorized[category]):
                count = len(unique_products[product])
                f.write(f"{product} (appears {count}x)\n")
        
        f.write(f"\n\nTotal unique products: {len(unique_products)}\n")
    
    print("✅ Done!")
    print()
    print(f"📊 Summary:")
    print(f"   - Total product mentions: {len(all_products)}")
    print(f"   - Unique products: {len(unique_products)}")
    print(f"   - Categories: {len(categorized)}")

"""
WHAT THIS SCRIPT DOES (Explanation):

1. READS the Word document with your meal plans
2. PARSES each line looking for product mentions
3. CLEANS product names (removes quantities, notes)
4. DEDUPLICATES to find unique products
5. CATEGORIZES products (Dairy, Protein, Vegetables, etc.)
6. SAVES a clean list to a text file

NEXT STEPS:
After running this, we'll:
- Review the list
- Find EAN barcodes for each product
- Add to database
"""
