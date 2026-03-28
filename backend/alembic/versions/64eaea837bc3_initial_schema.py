"""initial schema

Revision ID: 64eaea837bc3
Revises:
Create Date: 2026-03-24 21:19:41.357409

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "64eaea837bc3"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ingredient_categories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text, unique=True, nullable=False),
        sa.Column("slug", sa.Text, unique=True, nullable=False),
    )

    op.create_table(
        "ingredients",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("ingredient_categories.id")),
        sa.Column("source", sa.Text, server_default="manual", nullable=False),
        sa.Column("source_id", sa.Text),
        # Composition per 100g
        sa.Column("water_pct", sa.Numeric(8, 4)),
        sa.Column("total_fat_pct", sa.Numeric(8, 4)),
        sa.Column("saturated_fat_pct", sa.Numeric(8, 4)),
        sa.Column("trans_fat_pct", sa.Numeric(8, 4)),
        sa.Column("protein_pct", sa.Numeric(8, 4)),
        sa.Column("carbohydrate_pct", sa.Numeric(8, 4)),
        sa.Column("fiber_pct", sa.Numeric(8, 4)),
        sa.Column("total_sugar_pct", sa.Numeric(8, 4)),
        sa.Column("energy_kj_per_100g", sa.Numeric(10, 4)),
        sa.Column("alcohol_pct", sa.Numeric(8, 4)),
        sa.Column("sodium_mg", sa.Numeric(10, 4)),
        # Sugar breakdown
        sa.Column("sucrose_pct", sa.Numeric(8, 4)),
        sa.Column("glucose_pct", sa.Numeric(8, 4)),
        sa.Column("fructose_pct", sa.Numeric(8, 4)),
        sa.Column("lactose_pct", sa.Numeric(8, 4)),
        sa.Column("maltose_pct", sa.Numeric(8, 4)),
        sa.Column("galactose_pct", sa.Numeric(8, 4)),
        # Dairy-specific
        sa.Column("milk_fat_pct", sa.Numeric(8, 4)),
        sa.Column("msnf_pct", sa.Numeric(8, 4)),
        # Chocolate-specific
        sa.Column("cocoa_butter_pct", sa.Numeric(8, 4)),
        sa.Column("cocoa_solids_pct", sa.Numeric(8, 4)),
        # Stabilizer/emulsifier content per 100g
        sa.Column("stabilizer_pct", sa.Numeric(8, 4)),
        sa.Column("emulsifier_pct", sa.Numeric(8, 4)),
        # Overrides
        sa.Column("pac_override", sa.Numeric(10, 4)),
        sa.Column("pod_override", sa.Numeric(10, 4)),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "ingredient_aliases",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "ingredient_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ingredients.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("alias", sa.Text, nullable=False),
        sa.UniqueConstraint("ingredient_id", "alias"),
    )

    op.create_table(
        "target_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("alcohol_min", sa.Numeric(6, 2)),
        sa.Column("alcohol_max", sa.Numeric(6, 2)),
        sa.Column("serving_temp_min", sa.Numeric(6, 2)),
        sa.Column("serving_temp_max", sa.Numeric(6, 2)),
        sa.Column("sweetness_min", sa.Numeric(6, 2)),
        sa.Column("sweetness_max", sa.Numeric(6, 2)),
        sa.Column("total_solids_min", sa.Numeric(6, 2)),
        sa.Column("total_solids_max", sa.Numeric(6, 2)),
        sa.Column("total_fat_min", sa.Numeric(6, 2)),
        sa.Column("total_fat_max", sa.Numeric(6, 2)),
        sa.Column("milk_fat_min", sa.Numeric(6, 2)),
        sa.Column("milk_fat_max", sa.Numeric(6, 2)),
        sa.Column("sugar_min", sa.Numeric(6, 2)),
        sa.Column("sugar_max", sa.Numeric(6, 2)),
        sa.Column("msnf_min", sa.Numeric(6, 2)),
        sa.Column("msnf_max", sa.Numeric(6, 2)),
        sa.Column("stabilizer_min", sa.Numeric(6, 2)),
        sa.Column("stabilizer_max", sa.Numeric(6, 2)),
        sa.Column("emulsifier_min", sa.Numeric(6, 2)),
        sa.Column("emulsifier_max", sa.Numeric(6, 2)),
    )

    op.create_table(
        "recipes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("recipe_type", sa.Text),
        sa.Column(
            "target_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("target_profiles.id"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "recipe_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("recipes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "ingredient_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ingredients.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("weight_grams", sa.Numeric(10, 2), nullable=False),
        sa.Column("sort_order", sa.Integer, server_default="0", nullable=False),
        sa.UniqueConstraint("recipe_id", "ingredient_id"),
    )


def downgrade() -> None:
    op.drop_table("recipe_ingredients")
    op.drop_table("recipes")
    op.drop_table("target_profiles")
    op.drop_table("ingredient_aliases")
    op.drop_table("ingredients")
    op.drop_table("ingredient_categories")
