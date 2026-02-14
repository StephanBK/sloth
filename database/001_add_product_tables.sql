-- ============================================================================
-- SLOTH DATABASE MIGRATION: Add Product & Store Tables
-- ============================================================================
-- Date: 2025-02-14
-- Purpose: Extend existing Sloth database with product catalog and store availability
-- 
-- This migration adds:
-- 1. products table (master product catalog)
-- 2. product_availability table (which stores sell which products)
-- 3. product_alternatives table (substitutions when product unavailable)
-- 4. Links ingredients table to products
-- ============================================================================

-- ============================================================================
-- TABLE 1: PRODUCTS
-- ============================================================================
-- Stores the master catalog of ~46 core products used in meal plans
-- Each product has nutritional data and barcode (EAN) when available

CREATE TABLE IF NOT EXISTS products (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Product Identification
    name TEXT NOT NULL,
    brand TEXT,
    ean VARCHAR(13),  -- European Article Number (barcode), 13 digits
    
    -- Categorization
    category TEXT NOT NULL,  -- 'Dairy & Eggs', 'Protein - Meat & Fish', etc.
    
    -- Package Information
    package_size DECIMAL NOT NULL,  -- e.g., 500 for 500g
    unit TEXT NOT NULL,  -- 'g', 'ml', 'piece'
    
    -- Nutritional Data (per 100g/100ml)
    calories_per_100g DECIMAL,
    protein_per_100g DECIMAL,
    carbs_per_100g DECIMAL,
    fat_per_100g DECIMAL,
    fiber_per_100g DECIMAL,
    sugar_per_100g DECIMAL,
    salt_per_100g DECIMAL,
    
    -- Metadata
    notes TEXT,  -- e.g., "Various flavors available", "Used in 19+ plans"
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX idx_products_ean ON products(ean);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_name ON products(name);

COMMENT ON TABLE products IS 'Master catalog of products used in Sloth meal plans';
COMMENT ON COLUMN products.ean IS 'European Article Number (barcode) - 13 digits';
COMMENT ON COLUMN products.package_size IS 'Standard package size (e.g., 500 for 500g pack)';

-- ============================================================================
-- TABLE 2: PRODUCT_AVAILABILITY
-- ============================================================================
-- Tracks which supermarket chains carry which products
-- Enables "Find this product at Rewe 800m away" functionality

CREATE TABLE IF NOT EXISTS product_availability (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign Key to Products
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    
    -- Store Information
    store_chain TEXT NOT NULL,  -- 'REWE', 'Edeka', 'Lidl', 'Aldi', etc.
    
    -- Availability Status
    is_available BOOLEAN DEFAULT TRUE,
    last_verified DATE DEFAULT CURRENT_DATE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure unique combination of product + store
    CONSTRAINT unique_product_store UNIQUE(product_id, store_chain)
);

-- Create indexes for common queries
CREATE INDEX idx_availability_product ON product_availability(product_id);
CREATE INDEX idx_availability_store ON product_availability(store_chain);
CREATE INDEX idx_availability_status ON product_availability(is_available);

COMMENT ON TABLE product_availability IS 'Tracks which supermarkets carry which products';
COMMENT ON COLUMN product_availability.last_verified IS 'When we last confirmed this product is still available';

-- ============================================================================
-- TABLE 3: PRODUCT_ALTERNATIVES
-- ============================================================================
-- Suggests substitute products when the primary product is unavailable
-- E.g., "REWE Quarkcreme unavailable → use ja! High Protein Quark instead"

CREATE TABLE IF NOT EXISTS product_alternatives (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign Keys
    original_product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    alternative_product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    
    -- Alternative Metadata
    reason TEXT,  -- e.g., "Same macros, cheaper", "Available at more stores"
    priority INTEGER DEFAULT 1,  -- Lower number = better alternative
    
    -- Ensure original != alternative
    CONSTRAINT different_products CHECK (original_product_id != alternative_product_id),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX idx_alternatives_original ON product_alternatives(original_product_id);
CREATE INDEX idx_alternatives_priority ON product_alternatives(priority);

COMMENT ON TABLE product_alternatives IS 'Suggested substitutions when products are unavailable';
COMMENT ON COLUMN product_alternatives.priority IS 'Lower number = better alternative (1 is best)';

-- ============================================================================
-- TABLE 4: MODIFY EXISTING INGREDIENTS TABLE
-- ============================================================================
-- Add link from ingredients to products
-- This allows us to generate shopping lists with actual product barcodes

-- Check if column exists first (safe for re-running migration)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'ingredients' AND column_name = 'product_id'
    ) THEN
        ALTER TABLE ingredients 
            ADD COLUMN product_id UUID REFERENCES products(id);
        
        CREATE INDEX idx_ingredients_product ON ingredients(product_id);
        
        COMMENT ON COLUMN ingredients.product_id IS 'Links to specific product in catalog (optional - some ingredients are generic)';
    END IF;
END $$;

-- ============================================================================
-- HELPER VIEWS
-- ============================================================================
-- These make querying easier for the application

-- View: Products with store availability
CREATE OR REPLACE VIEW products_with_stores AS
SELECT 
    p.id,
    p.name,
    p.brand,
    p.ean,
    p.category,
    p.package_size,
    p.unit,
    ARRAY_AGG(DISTINCT pa.store_chain) FILTER (WHERE pa.is_available = TRUE) as available_at_stores,
    COUNT(DISTINCT pa.store_chain) FILTER (WHERE pa.is_available = TRUE) as num_stores
FROM products p
LEFT JOIN product_availability pa ON p.id = pa.product_id
GROUP BY p.id;

COMMENT ON VIEW products_with_stores IS 'Products with aggregated list of stores that carry them';

-- View: Products with alternatives
CREATE OR REPLACE VIEW products_with_alternatives AS
SELECT 
    p.id,
    p.name,
    p.brand,
    ARRAY_AGG(
        json_build_object(
            'id', alt.id,
            'name', alt.name,
            'brand', alt.brand,
            'reason', pa.reason,
            'priority', pa.priority
        ) ORDER BY pa.priority
    ) FILTER (WHERE alt.id IS NOT NULL) as alternatives
FROM products p
LEFT JOIN product_alternatives pa ON p.id = pa.original_product_id
LEFT JOIN products alt ON pa.alternative_product_id = alt.id
GROUP BY p.id;

COMMENT ON VIEW products_with_alternatives IS 'Products with their substitution options';

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Migration completed successfully!';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Added tables:';
    RAISE NOTICE '  - products';
    RAISE NOTICE '  - product_availability';
    RAISE NOTICE '  - product_alternatives';
    RAISE NOTICE 'Modified tables:';
    RAISE NOTICE '  - ingredients (added product_id column)';
    RAISE NOTICE 'Created views:';
    RAISE NOTICE '  - products_with_stores';
    RAISE NOTICE '  - products_with_alternatives';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Run import script to add 46 core products';
    RAISE NOTICE '  2. Add store availability data';
    RAISE NOTICE '  3. Link existing ingredients to products';
    RAISE NOTICE '============================================================';
END $$;
