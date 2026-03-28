"""SQLAlchemy ORM models for iscreami."""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class IngredientCategory(Base):
    __tablename__ = "ingredient_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    ingredients: Mapped[list["Ingredient"]] = relationship(back_populates="category")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingredient_categories.id")
    )
    source: Mapped[str] = mapped_column(Text, default="manual")
    source_id: Mapped[str | None] = mapped_column(Text)

    # Composition per 100g
    water_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    total_fat_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    saturated_fat_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    trans_fat_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    protein_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    carbohydrate_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    fiber_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    total_sugar_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    energy_kj_per_100g: Mapped[float | None] = mapped_column(Numeric(10, 4))
    alcohol_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    sodium_mg: Mapped[float | None] = mapped_column(Numeric(10, 4))

    # Sugar breakdown per 100g (nullable — advanced mode)
    sucrose_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    glucose_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    fructose_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    lactose_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    maltose_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    galactose_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))

    # Dairy-specific
    milk_fat_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    msnf_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))

    # Chocolate-specific
    cocoa_butter_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    cocoa_solids_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))

    # Stabilizer/emulsifier content per 100g
    stabilizer_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    emulsifier_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))

    # Optional manual overrides
    pac_override: Mapped[float | None] = mapped_column(Numeric(10, 4))
    pod_override: Mapped[float | None] = mapped_column(Numeric(10, 4))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    category: Mapped[IngredientCategory | None] = relationship(
        back_populates="ingredients"
    )
    aliases: Mapped[list["IngredientAlias"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="ingredient"
    )


class IngredientAlias(Base):
    __tablename__ = "ingredient_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
    )
    alias: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("ingredient_id", "alias"),)

    ingredient: Mapped["Ingredient"] = relationship(back_populates="aliases")


class TargetProfile(Base):
    __tablename__ = "target_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)

    serving_temp_min: Mapped[float | None] = mapped_column(Numeric(6, 2))
    serving_temp_max: Mapped[float | None] = mapped_column(Numeric(6, 2))
    sweetness_min: Mapped[float | None] = mapped_column(Numeric(6, 2))
    sweetness_max: Mapped[float | None] = mapped_column(Numeric(6, 2))
    total_solids_min: Mapped[float | None] = mapped_column(Numeric(6, 2))
    total_solids_max: Mapped[float | None] = mapped_column(Numeric(6, 2))
    total_fat_min: Mapped[float | None] = mapped_column(Numeric(6, 2))
    total_fat_max: Mapped[float | None] = mapped_column(Numeric(6, 2))
    milk_fat_min: Mapped[float | None] = mapped_column(Numeric(6, 2))
    milk_fat_max: Mapped[float | None] = mapped_column(Numeric(6, 2))
    sugar_min: Mapped[float | None] = mapped_column(Numeric(6, 2))
    sugar_max: Mapped[float | None] = mapped_column(Numeric(6, 2))
    alcohol_min: Mapped[float | None] = mapped_column(Numeric(6, 2))
    alcohol_max: Mapped[float | None] = mapped_column(Numeric(6, 2))
    msnf_min: Mapped[float | None] = mapped_column(Numeric(6, 2))
    msnf_max: Mapped[float | None] = mapped_column(Numeric(6, 2))
    stabilizer_min: Mapped[float | None] = mapped_column(Numeric(6, 2))
    stabilizer_max: Mapped[float | None] = mapped_column(Numeric(6, 2))
    emulsifier_min: Mapped[float | None] = mapped_column(Numeric(6, 2))
    emulsifier_max: Mapped[float | None] = mapped_column(Numeric(6, 2))

    recipes: Mapped[list["Recipe"]] = relationship(back_populates="target_profile")


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    recipe_type: Mapped[str | None] = mapped_column(Text)
    target_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("target_profiles.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    target_profile: Mapped[TargetProfile | None] = relationship(
        back_populates="recipes"
    )
    ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeIngredient.sort_order",
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (UniqueConstraint("recipe_id", "ingredient_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False
    )
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ingredients.id", ondelete="RESTRICT"),
        nullable=False,
    )
    weight_grams: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    recipe: Mapped[Recipe] = relationship(back_populates="ingredients")
    ingredient: Mapped[Ingredient] = relationship(back_populates="recipe_ingredients")
