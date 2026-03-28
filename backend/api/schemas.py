"""Pydantic v2 schemas for request/response models."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from api.services.composition import ingredient_total_solids_pct
from api.services.pac import ingredient_pac
from api.services.sweetness import ingredient_pod

# --- Enums ---


class MetricStatus(StrEnum):
    in_range = "in_range"
    below = "below"
    above = "above"


# --- Ingredient Category ---


class IngredientCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str


# --- Ingredient ---


class IngredientBase(BaseModel):
    name: str
    description: str | None = None
    category_id: int | None = None
    source: str = "manual"
    source_id: str | None = None

    # Composition per 100g
    water_pct: float | None = None
    total_fat_pct: float | None = None
    saturated_fat_pct: float | None = None
    trans_fat_pct: float | None = None
    protein_pct: float | None = None
    carbohydrate_pct: float | None = None
    fiber_pct: float | None = None
    total_sugar_pct: float | None = None
    energy_kj_per_100g: float | None = None
    alcohol_pct: float | None = None
    sodium_mg: float | None = None

    # Sugar breakdown
    sucrose_pct: float | None = None
    glucose_pct: float | None = None
    fructose_pct: float | None = None
    lactose_pct: float | None = None
    maltose_pct: float | None = None
    galactose_pct: float | None = None

    # Dairy-specific
    milk_fat_pct: float | None = None
    msnf_pct: float | None = None

    # Chocolate-specific
    cocoa_butter_pct: float | None = None
    cocoa_solids_pct: float | None = None

    # Stabilizer/emulsifier content per 100g
    stabilizer_pct: float | None = None
    emulsifier_pct: float | None = None

    # Overrides
    pac_override: float | None = None
    pod_override: float | None = None

    aliases: list[str] = []


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(IngredientBase):
    name: str | None = None  # type: ignore[assignment]


class IngredientOut(IngredientBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    category: IngredientCategoryOut | None = None

    @field_validator("aliases", mode="before")  # type: ignore[misc]
    @classmethod
    def coerce_aliases(cls, v: object) -> list[str]:
        if isinstance(v, list) and v and hasattr(v[0], "alias"):
            return [item.alias for item in v]  # type: ignore[union-attr]
        return v  # type: ignore[return-value]

    @computed_field  # type: ignore[misc]
    @property
    def pac(self) -> float:
        return ingredient_pac(self)  # type: ignore[arg-type]

    @computed_field  # type: ignore[misc]
    @property
    def pod(self) -> float:
        return ingredient_pod(self)  # type: ignore[arg-type]

    @computed_field  # type: ignore[misc]
    @property
    def total_solids_pct(self) -> float:
        return ingredient_total_solids_pct(self)  # type: ignore[arg-type]


class PaginatedIngredients(BaseModel):
    total: int
    items: list[IngredientOut]


# --- Target Profile ---


class TargetProfileBase(BaseModel):
    name: str
    serving_temp_min: float | None = None
    serving_temp_max: float | None = None
    sweetness_min: float | None = None
    sweetness_max: float | None = None
    total_solids_min: float | None = None
    total_solids_max: float | None = None
    total_fat_min: float | None = None
    total_fat_max: float | None = None
    milk_fat_min: float | None = None
    milk_fat_max: float | None = None
    sugar_min: float | None = None
    sugar_max: float | None = None
    alcohol_min: float | None = None
    alcohol_max: float | None = None
    msnf_min: float | None = None
    msnf_max: float | None = None
    stabilizer_min: float | None = None
    stabilizer_max: float | None = None
    emulsifier_min: float | None = None
    emulsifier_max: float | None = None


class TargetProfileCreate(TargetProfileBase):
    pass


class TargetProfileUpdate(TargetProfileBase):
    name: str | None = None  # type: ignore[assignment]


class TargetProfileOut(TargetProfileBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


# --- Recipe ---


class RecipeIngredientInput(BaseModel):
    ingredient_id: uuid.UUID
    weight_grams: float = Field(gt=0)
    sort_order: int = 0


class RecipeIngredientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ingredient_id: uuid.UUID
    weight_grams: float
    sort_order: int
    ingredient: IngredientOut


class RecipeCreate(BaseModel):
    name: str
    description: str | None = None
    recipe_type: str | None = None
    target_profile_id: uuid.UUID | None = None
    ingredients: list[RecipeIngredientInput] = []


class RecipeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    recipe_type: str | None = None
    target_profile_id: uuid.UUID | None = None
    ingredients: list[RecipeIngredientInput] | None = None


class RecipeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    description: str | None = None
    recipe_type: str | None = None
    target_profile_id: uuid.UUID | None = None
    target_profile: TargetProfileOut | None = None
    created_at: datetime
    updated_at: datetime
    ingredients: list[RecipeIngredientOut] = []

    @computed_field  # type: ignore
    @property
    def total_weight_grams(self) -> float:
        return sum(ingredient.weight_grams for ingredient in self.ingredients)


class PaginatedRecipes(BaseModel):
    total: int
    items: list[RecipeOut]


# --- Calculator ---


class CalculateIngredientInput(BaseModel):
    ingredient_id: uuid.UUID
    weight_grams: float = Field(gt=0)


class CalculateRequest(BaseModel):
    target_profile_id: uuid.UUID | None = None
    ingredients: list[CalculateIngredientInput] = Field(min_length=1)
    serving_size_g: float = 66.0


class CompositionResult(BaseModel):
    total_weight_g: float
    water_pct: float
    total_solids_pct: float
    total_fat_pct: float
    saturated_fat_pct: float
    trans_fat_pct: float
    milk_fat_pct: float
    msnf_pct: float
    total_sugar_pct: float
    protein_pct: float
    carbohydrate_pct: float
    fiber_pct: float
    alcohol_pct: float
    stabilizer_pct: float
    emulsifier_pct: float


class PACResult(BaseModel):
    pac_mix: float  # per 100g mix
    pac_water: float | None  # per 100g free water (None if no free water)


class FreezingCurvePoint(BaseModel):
    temperature_c: float
    frozen_water_pct: float


class FreezingResult(BaseModel):
    freezing_point_c: float
    serving_temperature_c: float | None
    curve: list[FreezingCurvePoint]


class SweetenerBreakdownItem(BaseModel):
    ingredient_name: str
    weight_g: float
    pct_of_sweeteners: float


class SweetnessResult(BaseModel):
    pod: float  # relative sweetness %
    sweetener_breakdown: list[SweetenerBreakdownItem]


class NutritionResult(BaseModel):
    per_100g: dict[str, float]
    per_serving: dict[str, float]
    serving_size_g: float


class MetricComparison(BaseModel):
    metric: str
    value: float
    target_min: float | None
    target_max: float | None
    status: MetricStatus


class CalculateResponse(BaseModel):
    composition: CompositionResult
    pac: PACResult
    freezing: FreezingResult
    sweetness: SweetnessResult
    nutrition: NutritionResult
    target_comparison: list[MetricComparison] | None = None


# --- Export/Import ---


class RecipeExportMetrics(BaseModel):
    """Calculated metrics in exported recipes."""

    model_config = ConfigDict(from_attributes=True)

    pac_mix: float
    pac_water: float | None = None
    pod: float
    freezing_point_c: float
    free_water_g: float
    sugar_solids_g: float


class RecipeExportOut(BaseModel):
    """Recipe as exported (includes calculated metrics and underscore keys)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    recipe_type: str | None = None
    created_at: str
    updated_at: str
    total_weight_grams: float
    target_profile: TargetProfileOut | None = None
    ingredients: list[RecipeIngredientOut] = []
    calculated_metrics: RecipeExportMetrics


# --- System ---


class HealthResponse(BaseModel):
    """Health check response."""

    status: str


class ImportErrorResponse(BaseModel):
    """Import error response with list of validation errors."""

    errors: list[str]
