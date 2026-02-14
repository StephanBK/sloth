# Open Food Facts - Understanding the Data

## What is Open Food Facts?

Open Food Facts (OFF) is a **crowd-sourced database** of food products from around the world. Think of it like Wikipedia for food products - anyone can contribute by scanning barcodes and uploading product info.

## Why are we using it?

1. **Free and Open** - No licensing fees
2. **Massive Coverage** - 100,000+ German products
3. **Rich Data** - Nutrition, ingredients, allergens, images
4. **Legal** - Explicitly designed for reuse

## The Data Format: JSONL

OFF provides their data as **JSONL** (JSON Lines):
- Each line is a complete JSON object representing one product
- Unlike regular JSON, we can read it line-by-line (memory efficient!)
- Example:

```json
{"code":"4337256250542","product_name":"Cornichons","brands":"Ja!","countries":"Germany","nutriments":{"energy-kcal_100g":15,"fat_100g":0.2,"carbohydrates_100g":2.1,"sugars_100g":1.8,"proteins_100g":0.5,"salt_100g":1.5},"nutriscore_grade":"a"}
```

## Key Fields We Care About

| Field | What it is | Example |
|-------|-----------|---------|
| `code` | Barcode (EAN-13) | "4337256250542" |
| `product_name` | Name in German | "Cornichons" |
| `brands` | Brand name | "Ja!" |
| `countries_tags` | Where sold | "en:germany" |
| `nutriments` | The nutrition object | See below ⬇️ |
| `nutriscore_grade` | A-E score | "a" |
| `stores` | Which stores sell it | "Rewe, Edeka" |

## The Nutriments Object (Most Important!)

This nested object contains all nutritional values per 100g:

```python
{
  "energy-kcal_100g": 15,      # Calories
  "energy-kj_100g": 63,         # Kilojoules
  "fat_100g": 0.2,              # Total fat
  "saturated-fat_100g": 0.05,   # Saturated fat
  "carbohydrates_100g": 2.1,    # Carbs
  "sugars_100g": 1.8,           # Sugars
  "proteins_100g": 0.5,         # Protein
  "salt_100g": 1.5,             # Salt
  "fiber_100g": 0.8             # Fiber (Ballaststoffe)
}
```

## Download URL

The full database is available at:
```
https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz
```

**Size:** ~7-8 GB compressed, ~30+ GB uncompressed
**German subset:** ~300-500 MB after filtering

## Next Steps

We'll write a Python script to:
1. Download this file
2. Read it line-by-line (not all at once!)
3. Filter for German products only
4. Save to our `data/raw/` folder
