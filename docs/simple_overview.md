# Sloth Diet App - Simple Overview

## What We're Building (Step-by-Step)

### Phase 1: Foundation (Where We Are Now) ✅
```
[Your Excel Plans] → [Database] → [App can query meals]
```

**What this means:**
- We take your 5 levels × 10 days = 50 meal plans
- Put them in a database
- App can say: "Show me Level 3, Day 1"

---

### Phase 2: Product Database (Next)
```
[~100 Products] → [Find Barcodes] → [Which Stores] → [Database]
```

**What this means:**
- Extract unique products from your plans
- Find their EAN barcodes
- Check which stores sell them
- Store in database

---

### Phase 3: Shopping List Generation
```
[User picks timeframe] → [App calculates products] → [Shows shopping list]
```

**Example:**
```
User: "I want 3 days, Level 3"
App: Queries Days 1-3
App: Adds up all products
App: Shows: "You need 6x Quarkcreme, 3x Rice, etc."
```

---

### Phase 4: Store Integration
```
[Shopping List] → [Check availability] → [Show stores + alternatives]
```

**Example:**
```
✅ REWE (800m): 15 items available
⚠️ Edeka (1.2km): 3 items here instead
💡 Alternatives: Substitute X with Y (same macros)
```

---

## The Database Tables (Simplified)

Think of it like Excel sheets that talk to each other:

### Sheet 1: MEAL_PLANS
```
| Level | Day | Meal | Calories | Protein | Carbs | Fat |
|-------|-----|------|----------|---------|-------|-----|
| 1     | 1   | 1    | 422      | 52      | 34    | 4   |
| 1     | 1   | 2    | 1088     | 102     | 126   | 18  |
```

### Sheet 2: MEAL_PLAN_ITEMS (What's IN each meal)
```
| Meal ID | Product               | Quantity |
|---------|-----------------------|----------|
| 1       | REWE Quarkcreme       | 200g     |
| 1       | Himbeer Heidelbeer Mix| 300g     |
```

### Sheet 3: PRODUCTS (Master product list)
```
| ID | Name                  | EAN           | Cal/100g | Protein | Carbs | Fat |
|----|-----------------------|---------------|----------|---------|-------|-----|
| 1  | REWE Quarkcreme       | 4337256300125 | 52       | 10.0    | 3.5   | 0.2 |
| 2  | Himbeer Heidelbeer Mix| 4337185417894 | 33       | 0.8     | 6.8   | 0.3 |
```

### Sheet 4: PRODUCT_AVAILABILITY (Where to buy)
```
| Product ID | Store | Available |
|------------|-------|-----------|
| 1          | REWE  | Yes       |
| 1          | Edeka | Yes       |
| 2          | REWE  | Yes       |
```

### Sheet 5: PRODUCT_ALTERNATIVES (Substitutions)
```
| Original Product    | Alternative Product | Reason           |
|---------------------|---------------------|------------------|
| REWE Quarkcreme     | ja! High Prot Quark | Same macros      |
| Wilhelm Hähnchen    | ja! Chicken Breast  | Cheaper, similar |
```

---

## How Data Flows (Example)

**User Action:**
"Show me shopping list for Level 3, Days 1-3"

**App Logic:**
1. Look in MEAL_PLANS: Get all meals for Level 3, Days 1-3
2. Look in MEAL_PLAN_ITEMS: See what products are needed
3. Add up quantities (Day 1 needs 200g Quarkcreme, Day 2 needs 200g → Total: 400g)
4. Look in PRODUCTS: Get product names and barcodes
5. Look in PRODUCT_AVAILABILITY: Check which stores have them
6. If missing: Look in PRODUCT_ALTERNATIVES: Suggest substitutes

**App Shows User:**
```
Shopping List (3 days)

REWE (800m) - 18 items:
□ 3x REWE High Protein Quarkcreme (200g each)
□ 2x Ben's Original Rice (125g each)
□ 600g REWE Bio Broccoli

Edeka (1.2km) - 2 items:
□ 400g Wilhelm Brandenburg Hähnchen
  (Or substitute: ja! Chicken Breast at REWE)
```

---

## Key Learning Concepts

### 1. **Database Tables = Organized Spreadsheets**
Each table stores one type of information

### 2. **Primary Keys (IDs)**
Each row gets a unique number so we can reference it
- Like row numbers in Excel, but guaranteed unique

### 3. **Foreign Keys (Links)**
One table references another
- MEAL_PLAN_ITEMS has `product_id` that points to PRODUCTS table
- Like VLOOKUP in Excel!

### 4. **Queries**
Asking the database questions
- "Give me all products where store = 'REWE'"
- Like filtering in Excel

### 5. **Joins**
Combining tables
- "Show me product names AND which stores sell them"
- Like combining two Excel sheets with VLOOKUP

---

## Next Concrete Step

Would you like to:

**Option A:** Create the database structure (empty tables, no data yet)
- I'll show you the SQL code
- Explain what each line does
- We can test it works

**Option B:** First extract the products from your Excel
- Parse the meal plans
- Make a list of unique products
- Then create database

**Option C:** Walk through a specific example
- "How would Level 3, Day 1 work?"
- Step-by-step with real data

Which would help you learn best?
