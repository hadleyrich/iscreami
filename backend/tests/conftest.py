"""Shared test fixtures for iscreami backend tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.models import (
    Base,
    Ingredient,
    IngredientCategory,
    Recipe,
    RecipeIngredient,
    TargetProfile,
)


def make_ingredient(**kwargs):
    """Create a mock Ingredient with sensible None defaults."""
    ingredient_name = kwargs.pop("name", "test")
    defaults = {
        "pac_override": None,
        "pod_override": None,
        "water_pct": None,
        "total_fat_pct": None,
        "total_sugar_pct": None,
        "protein_pct": None,
        "carbohydrate_pct": None,
        "sucrose_pct": None,
        "glucose_pct": None,
        "fructose_pct": None,
        "lactose_pct": None,
        "maltose_pct": None,
        "galactose_pct": None,
        "sodium_mg": None,
        "alcohol_pct": None,
        "stabilizer_pct": None,
        "emulsifier_pct": None,
        "milk_fat_pct": None,
        "msnf_pct": None,
        "saturated_fat_pct": None,
        "trans_fat_pct": None,
        "fiber_pct": None,
        "energy_kj_per_100g": None,
    }
    defaults.update(kwargs)
    mock = MagicMock()
    for key, value in defaults.items():
        setattr(mock, key, value)
    mock.name = ingredient_name
    return mock


def make_profile(**kwargs):
    """Create a mock TargetProfile with all bounds set to None by default."""
    defaults = {
        "total_solids_min": None,
        "total_solids_max": None,
        "total_fat_min": None,
        "total_fat_max": None,
        "milk_fat_max": None,
        "sugar_min": None,
        "sugar_max": None,
        "msnf_max": None,
        "stabilizer_min": None,
        "stabilizer_max": None,
        "emulsifier_min": None,
        "emulsifier_max": None,
        "sweetness_min": None,
        "sweetness_max": None,
        "serving_temp_min": None,
        "serving_temp_max": None,
    }
    defaults.update(kwargs)
    mock = MagicMock()
    for key, value in defaults.items():
        setattr(mock, key, value)
    return mock


@pytest.fixture
def ingredient():
    """Return the make_ingredient factory."""
    return make_ingredient


@pytest.fixture
def profile():
    """Return the make_profile factory."""
    return make_profile


# --- Database Fixtures (for integration tests) ---


@pytest.fixture(scope="function")
def test_db():
    """Create an in-memory SQLite database for integration tests.

    Scope: function (fresh DB for each test)
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    session_local = sessionmaker(bind=engine)
    session = session_local()

    yield session

    session.close()
    engine.dispose()


def make_ingredient_orm(db_session: Session, **kwargs) -> Ingredient:
    """Factory to create a real Ingredient ORM object in the database."""
    category_id = kwargs.pop("category_id", None)
    if category_id is None and kwargs.pop("create_category", False):
        cat = IngredientCategory(name="test", slug="test")
        db_session.add(cat)
        db_session.flush()
        category_id = cat.id

    ingredient = Ingredient(
        name=kwargs.pop("name", "Test Ingredient"),
        description=kwargs.pop("description", None),
        category_id=category_id,
        source=kwargs.pop("source", "manual"),
        source_id=kwargs.pop("source_id", None),
        water_pct=kwargs.pop("water_pct", None),
        total_fat_pct=kwargs.pop("total_fat_pct", None),
        total_sugar_pct=kwargs.pop("total_sugar_pct", 10.0),
        protein_pct=kwargs.pop("protein_pct", None),
        carbohydrate_pct=kwargs.pop("carbohydrate_pct", None),
        sodium_mg=kwargs.pop("sodium_mg", None),
        **kwargs,
    )
    db_session.add(ingredient)
    db_session.flush()
    return ingredient


def make_profile_orm(db_session: Session, **kwargs) -> TargetProfile:
    """Factory to create a real TargetProfile ORM object in the database."""
    profile = TargetProfile(
        name=kwargs.pop("name", "Test Profile"),
        serving_temp_min=kwargs.pop("serving_temp_min", None),
        serving_temp_max=kwargs.pop("serving_temp_max", None),
        sweetness_min=kwargs.pop("sweetness_min", None),
        sweetness_max=kwargs.pop("sweetness_max", None),
        total_solids_min=kwargs.pop("total_solids_min", None),
        total_solids_max=kwargs.pop("total_solids_max", None),
        total_fat_min=kwargs.pop("total_fat_min", None),
        total_fat_max=kwargs.pop("total_fat_max", None),
        milk_fat_min=kwargs.pop("milk_fat_min", None),
        milk_fat_max=kwargs.pop("milk_fat_max", None),
        sugar_min=kwargs.pop("sugar_min", None),
        sugar_max=kwargs.pop("sugar_max", None),
        alcohol_min=kwargs.pop("alcohol_min", None),
        alcohol_max=kwargs.pop("alcohol_max", None),
        msnf_min=kwargs.pop("msnf_min", None),
        msnf_max=kwargs.pop("msnf_max", None),
        stabilizer_min=kwargs.pop("stabilizer_min", None),
        stabilizer_max=kwargs.pop("stabilizer_max", None),
        emulsifier_min=kwargs.pop("emulsifier_min", None),
        emulsifier_max=kwargs.pop("emulsifier_max", None),
        **kwargs,
    )
    db_session.add(profile)
    db_session.flush()
    return profile


def make_recipe_orm(
    db_session: Session,
    ingredients: list[tuple[Ingredient, float]] | None = None,
    **kwargs,
) -> Recipe:
    """Factory to create a real Recipe ORM object in the database.

    Args:
        db_session: Database session
        ingredients: List of (Ingredient, weight_grams) tuples to add
        **kwargs: Other Recipe fields (name, description, etc.)
    """
    recipe = Recipe(
        name=kwargs.pop("name", "Test Recipe"),
        description=kwargs.pop("description", None),
        recipe_type=kwargs.pop("recipe_type", None),
        target_profile_id=kwargs.pop("target_profile_id", None),
        **kwargs,
    )
    db_session.add(recipe)
    db_session.flush()

    if ingredients:
        for idx, (ingredient, weight_g) in enumerate(ingredients):
            ri = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                weight_grams=weight_g,
                sort_order=idx,
            )
            db_session.add(ri)
        db_session.flush()

    return recipe


@pytest.fixture
def db_ingredient_factory(test_db: Session):
    """Factory fixture for creating real Ingredient objects."""

    def _factory(**kwargs) -> Ingredient:
        return make_ingredient_orm(test_db, **kwargs)

    return _factory


@pytest.fixture
def db_profile_factory(test_db: Session):
    """Factory fixture for creating real TargetProfile objects."""

    def _factory(**kwargs) -> TargetProfile:
        return make_profile_orm(test_db, **kwargs)

    return _factory


@pytest.fixture
def db_recipe_factory(test_db: Session):
    """Factory fixture for creating real Recipe objects."""

    def _factory(
        ingredients: list[tuple[Ingredient, float]] | None = None,
        **kwargs,
    ) -> Recipe:
        return make_recipe_orm(test_db, ingredients=ingredients, **kwargs)

    return _factory
