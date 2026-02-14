# Sloth Database Extension - Execution Guide

## 🎯 What We're Doing

Adding product catalog and store availability to your existing Sloth PostgreSQL database.

---

## 📋 Prerequisites

Before running these scripts, make sure you have:

✅ PostgreSQL database named 'sloth' (you already have this!)
✅ Your existing tables: users, meal_plans, meals, ingredients
✅ Database credentials (host, user, password)
✅ Python packages installed:
   ```bash
   pip install pandas psycopg2-binary
   ```

---

## 🚀 Step-by-Step Execution

### **Step 1: Run the Migration SQL**

This adds the new tables to your database.

**File:** `/home/claude/sloth/database/001_add_product_tables.sql`

**How to run:**

**Option A - Using psql command line:**
```bash
psql -U postgres -d sloth -f /home/claude/sloth/database/001_add_product_tables.sql
```

**Option B - Using a database GUI (pgAdmin, DBeaver, etc.):**
1. Open your database tool
2. Connect to the 'sloth' database
3. Open the SQL file
4. Execute it

**Option C - Using Python:**
```python
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='sloth',
    user='postgres',
    password='your_password'
)

with open('/home/claude/sloth/database/001_add_product_tables.sql', 'r') as f:
    sql = f.read()
    
cursor = conn.cursor()
cursor.execute(sql)
conn.commit()
conn.close()

print("Migration complete!")
```

**What this does:**
- Creates `products` table
- Creates `product_availability` table
- Creates `product_alternatives` table
- Adds `product_id` column to your existing `ingredients` table
- Creates helpful views for querying

**Expected output:**
```
NOTICE:  ============================================================
NOTICE:  Migration completed successfully!
NOTICE:  ============================================================
```

---

### **Step 2: Import the 46 Core Products**

**File:** `/home/claude/sloth/scripts/03_import_products.py`

**Before running:**
1. Edit the DB_CONFIG in the script OR set environment variables:
   ```bash
   export DB_HOST=localhost
   export DB_NAME=sloth
   export DB_USER=postgres
   export DB_PASSWORD=your_password
   ```

**Run the script:**
```bash
python3 /home/claude/sloth/scripts/03_import_products.py
```

**What this does:**
- Reads `/home/claude/sloth/data/processed/core_products.csv`
- Connects to your PostgreSQL database
- Inserts all 46 products
- Verifies the import

**Expected output:**
```
======================================================================
SLOTH PRODUCT IMPORTER
======================================================================

🔌 Connecting to database: sloth@localhost
✅ Connected successfully!
📖 Reading CSV: /home/claude/sloth/data/processed/core_products.csv
✅ Loaded 46 products
📊 Columns: product_id, category, name, brand, package_size, unit, ean, notes

🚀 Starting import...
📥 Inserting 46 products...

✅ Successfully inserted 46 products:
   - ja! Skyr natur (ID: abc123...)
   - ja! Magerquark (ID: def456...)
   ... and 41 more

💾 Transaction committed!

🔍 Verifying import...
   Total products in database: 46
   
   Products by category:
      Dairy & Eggs: 7
      Protein - Meat & Fish: 4
      Protein - Plant-based: 6
      Grains & Cereals: 5
      Vegetables & Frozen Veg: 6
      Frozen Meals: 7
      Canned & Shelf-stable: 3
      Fruit & Snacks: 5
      Pantry: 3
   
   Products with EAN barcodes: 0/46
   
   ⚠️  Warning: 46 products missing nutritional data
      Next step: Add nutrition data for these products

🎉 Import complete!
```

---

### **Step 3: Verify in Database**

Check that everything worked:

```sql
-- Count products
SELECT COUNT(*) FROM products;
-- Should return: 46

-- View first few products
SELECT name, brand, category, package_size, unit
FROM products
LIMIT 10;

-- Check the new column in ingredients
\d ingredients
-- Should show: product_id | uuid | 

-- Use the helpful view
SELECT name, available_at_stores
FROM products_with_stores
LIMIT 5;
```

---

## ⚠️ Troubleshooting

### **"relation products already exists"**
You've already run the migration. That's fine! The script is safe to re-run.

### **"permission denied for database sloth"**
Make sure your database user has CREATE permissions:
```sql
GRANT ALL PRIVILEGES ON DATABASE sloth TO your_username;
```

### **"psycopg2 module not found"**
Install it:
```bash
pip install psycopg2-binary
```

### **"Connection refused"**
PostgreSQL isn't running. Start it:
```bash
# Mac
brew services start postgresql

# Linux
sudo systemctl start postgresql
```

---

## 📊 What You'll Have After This

### **New Tables:**
```
products (46 rows)
├── id, name, brand, ean
├── category, package_size, unit
└── calories_per_100g, protein_per_100g, etc.

product_availability (0 rows initially)
├── product_id, store_chain
└── is_available, last_verified

product_alternatives (0 rows initially)
├── original_product_id, alternative_product_id
└── reason, priority
```

### **Modified Table:**
```
ingredients
└── + product_id column (links to products table)
```

---

## 🎯 Next Steps

After completing Steps 1 & 2:

1. **Add nutritional data** for the 46 products
   - Option A: Manually from product websites
   - Option B: Use Open Food Facts API (we have the script ready)
   
2. **Add store availability**
   - Mark which products are at REWE, Edeka, Lidl, etc.
   
3. **Link existing ingredients to products**
   - Update your existing `ingredients` rows to reference `product_id`

---

## 💡 Tips

- **Backup first!** Always backup before migrations:
  ```bash
  pg_dump sloth > sloth_backup_$(date +%Y%m%d).sql
  ```

- **Test on copy:** If nervous, test on a copy of your database first

- **Check logs:** PostgreSQL logs are your friend for debugging

---

## 📞 Questions?

If something doesn't work:
1. Check the error message carefully
2. Verify PostgreSQL is running
3. Confirm database credentials
4. Make sure you have the prerequisite Python packages

Ready to run these? Let me know how it goes! 🐌
