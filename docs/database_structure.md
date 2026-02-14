# Sloth Diet - Database Structure Design

## 🎯 Goal
Store meal plans and products in a way that's:
- Easy to query ("Show me Level 3, Day 1")
- Flexible (can add more products/levels later)
- Supports alternatives ("If X not available, suggest Y")

---

## 📊 Database Tables (Simplified)

### **Table 1: MEAL_PLANS**
Stores the complete meal plans from your Excel

| Column | Type | Example | Why? |
|--------|------|---------|------|
| `plan_id` | Integer | 1 | Unique ID |
| `level` | Integer | 3 | Which calorie level (1-5) |
| `day` | Integer | 1 | Which day (1-10) |
| `meal_number` | Integer | 1 | Breakfast=1, Lunch=2, etc. |
| `target_calories` | Integer | 460 | Calories for this meal |
| `target_protein` | Integer | 56 | Protein (g) |
| `target_carbs` | Integer | 40 | Carbs (g) |
| `target_fat` | Integer | 3 | Fat (g) |

**Example Row:**
```
plan_id: 1
level: 1
day: 1
meal_number: 1
target_calories: 422
target_protein: 52
target_carbs: 34
target_fat: 4
```

---

### **Table 2: MEAL_PLAN_ITEMS**
What products are in each meal

| Column | Type | Example | Why? |
|--------|------|---------|------|
| `item_id` | Integer | 1 | Unique ID |
| `plan_id` | Integer | 1 | Links to MEAL_PLANS table |
| `product_id` | Integer | 42 | Links to PRODUCTS table |
| `quantity` | Decimal | 200 | How much (in grams/ml) |
| `preparation_note` | Text | "1 EL Olivenöl zum Braten" | Optional cooking instruction |

**Example Row:**
```
item_id: 1
plan_id: 1
product_id: 42  (this is the REWE High Protein Quarkcreme)
quantity: 200
preparation_note: null
```

---

### **Table 3: PRODUCTS**
The master product database

| Column | Type | Example | Why? |
|--------|------|---------|------|
| `product_id` | Integer | 42 | Unique ID |
| `name` | Text | "REWE Beste Wahl High Protein Quarkcreme Vanille" | Full product name |
| `brand` | Text | "REWE Beste Wahl" | Brand |
| `ean` | Text | "4337256123456" | Barcode (13 digits) |
| `calories_per_100g` | Decimal | 52 | Nutrition per 100g |
| `protein_per_100g` | Decimal | 10.0 | Protein per 100g |
| `carbs_per_100g` | Decimal | 3.5 | Carbs per 100g |
| `fat_per_100g` | Decimal | 0.2 | Fat per 100g |
| `default_serving_size` | Integer | 200 | Common portion (g) |

**Example Row:**
```
product_id: 42
name: "REWE Beste Wahl High Protein Quarkcreme"
brand: "REWE Beste Wahl"
ean: "4337256300125"
calories_per_100g: 52
protein_per_100g: 10.0
carbs_per_100g: 3.5
fat_per_100g: 0.2
default_serving_size: 200
```

---

### **Table 4: PRODUCT_AVAILABILITY**
Which stores sell which products

| Column | Type | Example | Why? |
|--------|------|---------|------|
| `availability_id` | Integer | 1 | Unique ID |
| `product_id` | Integer | 42 | Links to PRODUCTS |
| `store_chain` | Text | "REWE" | Which chain |
| `is_available` | Boolean | TRUE | Still in stock/discontinued |
| `last_verified` | Date | 2025-02-14 | When we last checked |

**Example Row:**
```
availability_id: 1
product_id: 42
store_chain: "REWE"
is_available: TRUE
last_verified: 2025-02-14
```

---

### **Table 5: PRODUCT_ALTERNATIVES**
Substitutions when product unavailable

| Column | Type | Example | Why? |
|--------|------|---------|------|
| `alternative_id` | Integer | 1 | Unique ID |
| `original_product_id` | Integer | 42 | The ideal product |
| `alternative_product_id` | Integer | 87 | The substitute |
| `reason` | Text | "Same macros, cheaper" | Why this alternative |
| `priority` | Integer | 1 | Best alternative = 1 |

**Example Row:**
```
alternative_id: 1
original_product_id: 42  (REWE High Protein Quarkcreme)
alternative_product_id: 87  (ja! High Protein Quark)
reason: "Similar macros, available at more stores"
priority: 1
```

---

## 🔄 How It All Connects

```
User picks: Level 3, Day 1, Shopping for 3 days

1. Query MEAL_PLANS: Get all meals for Level 3, Days 1-3
   ↓
2. Query MEAL_PLAN_ITEMS: Get all products needed
   ↓
3. Query PRODUCTS: Get details (name, barcode, nutrition)
   ↓
4. Query PRODUCT_AVAILABILITY: Check which stores have them
   ↓
5. If product unavailable: Query PRODUCT_ALTERNATIVES
   ↓
6. Generate shopping list with alternatives
```

---

## 📝 Example Query Flow

**User Request:** "Show me shopping list for Level 3, Days 1-3"

**Step 1:** Get all meals
```sql
SELECT * FROM MEAL_PLANS 
WHERE level = 3 AND day IN (1, 2, 3)
```

**Step 2:** Get all products needed
```sql
SELECT product_id, SUM(quantity) as total_quantity
FROM MEAL_PLAN_ITEMS
WHERE plan_id IN (previous results)
GROUP BY product_id
```

**Step 3:** Get product details and availability
```sql
SELECT p.name, p.ean, pa.store_chain
FROM PRODUCTS p
JOIN PRODUCT_AVAILABILITY pa ON p.product_id = pa.product_id
WHERE p.product_id IN (previous results)
```

---

## 🎨 User Experience Example

**App Display:**
```
Shopping List for 3 Days (Level 3, Days 1-3)

✅ Available at REWE (800m):
  - 6x REWE Beste Wahl High Protein Quarkcreme (200g)
  - 3x Ben's Original Spitzen Langkorn Reis (125g)
  - 900g REWE Bio Broccoli

⚠️ Not at REWE, try Edeka (1.2km):
  - 2x Wilhelm Brandenburg Hähnchen Minutenschnitzel (400g)
    Alternative: ja! Hähnchen Filet (similar macros)

❌ Not found nearby:
  - Salakis Feta Light
    Alternative: Milkana Feta Light (at Lidl 1.5km)
```

---

## 🚀 Next Steps

1. Create the database (SQLite for now, easy to migrate later)
2. Import your meal plans from Excel into MEAL_PLANS table
3. Extract unique products and populate PRODUCTS table
4. Find EAN codes for each product
5. Add store availability data

**Question for you:** Does this structure make sense? Any changes you'd want?
