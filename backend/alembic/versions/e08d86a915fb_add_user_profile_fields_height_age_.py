"""Add user profile fields: height, age, weight, activity, dietary, intake_completed

Revision ID: e08d86a915fb
Revises: 7088d5175c9f
Create Date: 2026-02-03 04:55:43.333432

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e08d86a915fb'
down_revision: Union[str, Sequence[str], None] = '7088d5175c9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Create the ENUM type for activity level
activitylevel_enum = postgresql.ENUM('SEDENTARY', 'LIGHT', 'MODERATE', 'ACTIVE', name='activitylevel', create_type=False)


def upgrade() -> None:
    """Upgrade schema."""
    # Create the ENUM type first
    activitylevel_enum.create(op.get_bind(), checkfirst=True)

    # Add new columns
    op.add_column('users', sa.Column('height_cm', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('current_weight_kg', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('goal_weight_kg', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('starting_weight_kg', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('activity_level', activitylevel_enum, nullable=True))
    op.add_column('users', sa.Column('dietary_restrictions', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('intake_completed', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('users', sa.Column('profile_picture_url', sa.String(length=500), nullable=True))

    # Allow gender to be nullable (for users who haven't completed intake)
    op.alter_column('users', 'gender',
               existing_type=postgresql.ENUM('MALE', 'FEMALE', name='gender'),
               nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'gender',
               existing_type=postgresql.ENUM('MALE', 'FEMALE', name='gender'),
               nullable=False)
    op.drop_column('users', 'profile_picture_url')
    op.drop_column('users', 'intake_completed')
    op.drop_column('users', 'dietary_restrictions')
    op.drop_column('users', 'activity_level')
    op.drop_column('users', 'starting_weight_kg')
    op.drop_column('users', 'goal_weight_kg')
    op.drop_column('users', 'current_weight_kg')
    op.drop_column('users', 'age')
    op.drop_column('users', 'height_cm')

    # Drop the ENUM type
    activitylevel_enum.drop(op.get_bind(), checkfirst=True)
