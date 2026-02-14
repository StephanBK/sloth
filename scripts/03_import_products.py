#!/usr/bin/env python3
"""
Script: Import Core Products to Sloth Database

This script imports the 46 curated products from our CSV into the PostgreSQL database.

Prerequisites:
- Migration 001_add_product_tables.sql must be run first
- PostgreSQL connection details in environment variables

Learning Points:
- Connecting to PostgreSQL with psycopg2
- Reading CSV files with pandas
- Bulk INSERT operations
- Transaction management (commit/rollback)

Author: Stephan & Claude
Date: 2025-02-14
"""

import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import os
from datetime import datetime

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# CSV file with our 46 products
CSV_FILE = "/home/claude/sloth/data/processed/core_products.csv"

# PostgreSQL connection details
# TODO: Replace these with your actual database credentials
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'sloth'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'your_password_here')
}

# ==============================================================================
# DATABASE CONNECTION
# ==============================================================================

def connect_to_database():
    """
    Create a connection to the PostgreSQL database.
    
    Returns:
        connection: psycopg2 connection object
        
    Raises:
        Exception: If connection fails
        
    Learning Note:
    psycopg2 is the most popular PostgreSQL adapter for Python.
    It allows us to execute SQL commands from Python code.
    """
    try:
        print(f"🔌 Connecting to database: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
        
        conn = psycopg2.connect(**DB_CONFIG)
        
        print("✅ Connected successfully!")
        return conn
        
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        raise

# ==============================================================================
# DATA LOADING
# ==============================================================================

def load_products_from_csv(csv_path):
    """
    Load products from CSV file using pandas.
    
    Args:
        csv_path (str): Path to the CSV file
        
    Returns:
        DataFrame: Pandas dataframe with product data
        
    Learning Note:
    pandas is excellent for working with CSV data.
    It automatically handles types, missing values, etc.
    """
    print(f"📖 Reading CSV: {csv_path}")
    
    # Read CSV into pandas DataFrame
    df = pd.read_csv(csv_path)
    
    print(f"✅ Loaded {len(df)} products")
    print(f"📊 Columns: {', '.join(df.columns)}")
    
    return df

# ==============================================================================
# DATA IMPORT
# ==============================================================================

def import_products(conn, df):
    """
    Import products into the database.
    
    Args:
        conn: Database connection
        df: DataFrame with product data
        
    Learning Notes:
    - cursor.execute() runs a single SQL command
    - execute_values() efficiently inserts many rows at once
    - Transactions: changes aren't saved until conn.commit()
    - If error occurs, conn.rollback() undoes all changes
    """
    cursor = conn.cursor()
    
    try:
        print("\n🚀 Starting import...")
        
        # Prepare data for insertion
        # We need to convert DataFrame rows to tuples
        products_data = []
        
        for _, row in df.iterrows():
            # Build tuple for INSERT
            # (name, brand, category, package_size, unit, ean, notes)
            product = (
                row['name'],
                row['brand'],
                row['category'],
                float(row['package_size']),
                row['unit'],
                row['ean'] if pd.notna(row['ean']) else None,  # Handle empty EAN
                row['notes'] if pd.notna(row['notes']) else None
            )
            products_data.append(product)
        
        # SQL INSERT statement
        insert_query = """
            INSERT INTO products 
                (name, brand, category, package_size, unit, ean, notes)
            VALUES %s
            RETURNING id, name
        """
        
        # Execute bulk insert
        print(f"📥 Inserting {len(products_data)} products...")
        
        result = execute_values(
            cursor, 
            insert_query, 
            products_data,
            page_size=100,  # Insert in batches of 100
            fetch=True  # Return the inserted rows
        )
        
        # Show what was inserted
        print(f"\n✅ Successfully inserted {len(result)} products:")
        for product_id, product_name in result[:5]:  # Show first 5
            print(f"   - {product_name} (ID: {product_id})")
        
        if len(result) > 5:
            print(f"   ... and {len(result) - 5} more")
        
        # COMMIT the transaction
        # This makes the changes permanent
        conn.commit()
        print("\n💾 Transaction committed!")
        
        return result
        
    except Exception as e:
        # If anything goes wrong, ROLLBACK
        # This undoes all changes in this transaction
        print(f"\n❌ Error during import: {e}")
        conn.rollback()
        print("🔄 Transaction rolled back")
        raise
        
    finally:
        cursor.close()

# ==============================================================================
# VERIFICATION
# ==============================================================================

def verify_import(conn):
    """
    Verify that products were imported correctly.
    
    Args:
        conn: Database connection
        
    Learning Note:
    Always verify your data after import!
    Count records, check for nulls, etc.
    """
    cursor = conn.cursor()
    
    try:
        print("\n🔍 Verifying import...")
        
        # Count total products
        cursor.execute("SELECT COUNT(*) FROM products")
        total_count = cursor.fetchone()[0]
        print(f"   Total products in database: {total_count}")
        
        # Count by category
        cursor.execute("""
            SELECT category, COUNT(*) 
            FROM products 
            GROUP BY category 
            ORDER BY COUNT(*) DESC
        """)
        
        print("\n   Products by category:")
        for category, count in cursor.fetchall():
            print(f"      {category}: {count}")
        
        # Check for products with EAN codes
        cursor.execute("""
            SELECT COUNT(*) 
            FROM products 
            WHERE ean IS NOT NULL
        """)
        with_ean = cursor.fetchone()[0]
        print(f"\n   Products with EAN barcodes: {with_ean}/{total_count}")
        
        # Check for products without nutritional data
        cursor.execute("""
            SELECT COUNT(*) 
            FROM products 
            WHERE calories_per_100g IS NULL
        """)
        without_nutrition = cursor.fetchone()[0]
        
        if without_nutrition > 0:
            print(f"\n   ⚠️  Warning: {without_nutrition} products missing nutritional data")
            print(f"      Next step: Add nutrition data for these products")
        else:
            print(f"\n   ✅ All products have nutritional data")
        
    finally:
        cursor.close()

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("SLOTH PRODUCT IMPORTER")
    print("="*70)
    print()
    
    # Step 1: Load CSV
    try:
        df = load_products_from_csv(CSV_FILE)
    except FileNotFoundError:
        print(f"❌ CSV file not found: {CSV_FILE}")
        exit(1)
    
    # Step 2: Connect to database
    try:
        conn = connect_to_database()
    except Exception:
        print("\n💡 Make sure:")
        print("   1. PostgreSQL is running")
        print("   2. Database 'sloth' exists")
        print("   3. Migration 001_add_product_tables.sql was run")
        print("   4. Environment variables are set correctly")
        exit(1)
    
    # Step 3: Import products
    try:
        imported = import_products(conn, df)
    except Exception:
        print("\n❌ Import failed")
        exit(1)
    
    # Step 4: Verify
    verify_import(conn)
    
    # Step 5: Close connection
    conn.close()
    print("\n🎉 Import complete!")
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Add nutritional data for products")
    print("2. Add store availability data")
    print("3. Link existing meal plan ingredients to products")
    print("="*70)

"""
HOW TO RUN THIS SCRIPT:

1. Set environment variables (or edit DB_CONFIG above):
   export DB_HOST=localhost
   export DB_NAME=sloth
   export DB_USER=postgres
   export DB_PASSWORD=your_password

2. Install required packages:
   pip install pandas psycopg2-binary

3. Run the script:
   python3 /home/claude/sloth/scripts/03_import_products.py

WHAT THIS SCRIPT DOES:

1. Reads the core_products.csv file
2. Connects to your PostgreSQL database
3. Inserts all 46 products into the 'products' table
4. Verifies the import was successful
5. Shows summary statistics

LEARNING CONCEPTS:

- Database Connections: How to connect Python to PostgreSQL
- Transactions: Changes aren't permanent until commit()
- Bulk Inserts: execute_values() is much faster than individual INSERTs
- Error Handling: try/except/finally ensures cleanup happens
- Data Verification: Always check your imports!
"""
