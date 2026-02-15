"""Add data pipeline columns and product_source_links table

Revision ID: c4a1f2d89e3b
Revises: b39bb66bf7a7
Create Date: 2026-02-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4a1f2d89e3b'
down_revision: Union[str, None] = 'b39bb66bf7a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Add new columns to products table ---

    # Data provenance
    op.add_column('products', sa.Column('data_source', sa.String(50), nullable=True))
    op.add_column('products', sa.Column('data_confidence', sa.Float(), nullable=True))
    op.add_column('products', sa.Column('is_curated', sa.Boolean(), nullable=True))

    # External identifiers
    op.add_column('products', sa.Column('off_id', sa.String(50), nullable=True))
    op.add_column('products', sa.Column('bls_code', sa.String(20), nullable=True))

    # Quality/display fields
    op.add_column('products', sa.Column('nutriscore_grade', sa.String(1), nullable=True))
    op.add_column('products', sa.Column('image_url', sa.String(500), nullable=True))
    op.add_column('products', sa.Column('image_thumb_url', sa.String(500), nullable=True))

    # Sync tracking
    op.add_column('products', sa.Column('last_synced_at', sa.DateTime(), nullable=True))

    # Make package_size and unit nullable for bulk imports
    op.alter_column('products', 'package_size', existing_type=sa.Float(), nullable=True)
    op.alter_column('products', 'unit', existing_type=sa.String(50), nullable=True)

    # Backfill existing products as manual/curated
    op.execute("UPDATE products SET data_source = 'manual', is_curated = true, data_confidence = 1.0")

    # Now set NOT NULL on data_source and is_curated with defaults
    op.alter_column('products', 'data_source',
                    existing_type=sa.String(50),
                    nullable=False,
                    server_default='manual')
    op.alter_column('products', 'is_curated',
                    existing_type=sa.Boolean(),
                    nullable=False,
                    server_default=sa.text('false'))

    # Indexes on products
    op.create_index('idx_products_data_source', 'products', ['data_source'])
    op.create_index('idx_products_off_id', 'products', ['off_id'])
    op.create_index('idx_products_bls_code', 'products', ['bls_code'])

    # --- Create product_source_links table ---
    op.create_table(
        'product_source_links',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('product_id', sa.String(36),
                  sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('external_id', sa.String(100), nullable=False),
        sa.Column('external_data', sa.Text(), nullable=True),
        sa.Column('matched_at', sa.DateTime(), nullable=False),
        sa.Column('match_method', sa.String(50), nullable=True),
        sa.Column('match_confidence', sa.Float(), nullable=True),
    )


def downgrade() -> None:
    # Drop product_source_links table
    op.drop_table('product_source_links')

    # Drop indexes
    op.drop_index('idx_products_bls_code', table_name='products')
    op.drop_index('idx_products_off_id', table_name='products')
    op.drop_index('idx_products_data_source', table_name='products')

    # Restore package_size and unit to NOT NULL
    op.alter_column('products', 'package_size', existing_type=sa.Float(), nullable=False)
    op.alter_column('products', 'unit', existing_type=sa.String(50), nullable=False)

    # Remove server defaults before dropping columns
    op.alter_column('products', 'data_source',
                    existing_type=sa.String(50),
                    server_default=None)
    op.alter_column('products', 'is_curated',
                    existing_type=sa.Boolean(),
                    server_default=None)

    # Drop new columns
    op.drop_column('products', 'last_synced_at')
    op.drop_column('products', 'image_thumb_url')
    op.drop_column('products', 'image_url')
    op.drop_column('products', 'nutriscore_grade')
    op.drop_column('products', 'bls_code')
    op.drop_column('products', 'off_id')
    op.drop_column('products', 'is_curated')
    op.drop_column('products', 'data_confidence')
    op.drop_column('products', 'data_source')
