"""Tests for recipe export/import service."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class TestNormalizeImportData:
    def test_single_object_wrapped_in_list(self):
        from api.services.export import normalize_import_data

        data = {"name": "Test Recipe"}
        assert normalize_import_data(data) == [data]

    def test_list_returned_unchanged(self):
        from api.services.export import normalize_import_data

        data = [{"name": "Recipe 1"}, {"name": "Recipe 2"}]
        assert normalize_import_data(data) == data

    def test_empty_list_returned_unchanged(self):
        from api.services.export import normalize_import_data

        assert normalize_import_data([]) == []

    def test_invalid_type_raises_value_error(self):
        from api.services.export import normalize_import_data

        with pytest.raises(ValueError):
            normalize_import_data("invalid")  # type: ignore[arg-type]

    def test_none_raises_value_error(self):
        from api.services.export import normalize_import_data

        with pytest.raises(ValueError):
            normalize_import_data(None)  # type: ignore[arg-type]

    def test_integer_raises_value_error(self):
        from api.services.export import normalize_import_data

        with pytest.raises(ValueError):
            normalize_import_data(42)  # type: ignore[arg-type]


class TestValidateImportData:
    def _db(self):
        from sqlalchemy.orm import Session

        return MagicMock(spec=Session)

    def test_empty_list_rejected(self):
        from api.services.export import validate_import_data

        errors = validate_import_data([], self._db())
        assert len(errors) > 0
        assert any("at least one recipe" in e for e in errors)

    def test_missing_name_rejected(self):
        from api.services.export import validate_import_data

        errors = validate_import_data([{"ingredients": []}], self._db())
        assert any("name is required" in e for e in errors)

    def test_empty_name_rejected(self):
        from api.services.export import validate_import_data

        errors = validate_import_data([{"name": "", "ingredients": []}], self._db())
        assert any("name is required" in e for e in errors)

    def test_valid_recipe_no_ingredients(self):
        from api.services.export import validate_import_data

        errors = validate_import_data(
            [{"name": "Simple", "ingredients": []}], self._db()
        )
        assert errors == []

    def test_missing_ingredient_id_rejected(self):
        from api.services.export import validate_import_data

        data = [{"name": "Test", "ingredients": [{"weight_grams": 100}]}]
        errors = validate_import_data(data, self._db())
        assert any("ingredient_id is required" in e for e in errors)

    def test_invalid_uuid_rejected(self):
        from api.services.export import validate_import_data

        data = [
            {
                "name": "Test",
                "ingredients": [{"ingredient_id": "not-a-uuid", "weight_grams": 100}],
            }
        ]
        errors = validate_import_data(data, self._db())
        assert any("invalid UUID" in e for e in errors)

    def test_negative_weight_rejected(self):
        from api.services.export import validate_import_data

        data = [
            {
                "name": "Test",
                "ingredients": [
                    {
                        "ingredient_id": "550e8400-e29b-41d4-a716-446655440000",
                        "weight_grams": -5,
                    }
                ],
            }
        ]
        errors = validate_import_data(data, self._db())
        assert any("positive number" in e for e in errors)

    def test_zero_weight_rejected(self):
        from api.services.export import validate_import_data

        data = [
            {
                "name": "Test",
                "ingredients": [
                    {
                        "ingredient_id": "550e8400-e29b-41d4-a716-446655440000",
                        "weight_grams": 0,
                    }
                ],
            }
        ]
        errors = validate_import_data(data, self._db())
        assert any("positive number" in e for e in errors)

    def test_missing_weight_grams_rejected(self):
        from api.services.export import validate_import_data

        data = [
            {
                "name": "Test",
                "ingredients": [
                    {"ingredient_id": "550e8400-e29b-41d4-a716-446655440000"}
                ],
            }
        ]
        errors = validate_import_data(data, self._db())
        assert any("weight_grams is required" in e for e in errors)

    def test_ingredient_not_found_in_db_rejected(self):
        from api.services.export import validate_import_data

        db = self._db()
        # Simulate DB returning nothing for scalars().first()
        db.scalars.return_value.first.return_value = None

        data = [
            {
                "name": "Test",
                "ingredients": [
                    {
                        "ingredient_id": "550e8400-e29b-41d4-a716-446655440000",
                        "weight_grams": 100,
                    }
                ],
            }
        ]
        errors = validate_import_data(data, db)
        assert any("ingredient not found" in e for e in errors)

    def test_multiple_recipes_accumulates_errors(self):
        from api.services.export import validate_import_data

        data = [{"ingredients": []}, {"ingredients": []}]  # both missing name
        errors = validate_import_data(data, self._db())
        # Should have at least one error per recipe
        assert len([e for e in errors if "name is required" in e]) >= 2

    def test_ingredients_not_list_rejected(self):
        from api.services.export import validate_import_data

        data = [{"name": "Test", "ingredients": "not-a-list"}]
        errors = validate_import_data(data, self._db())
        assert any("ingredients must be an array" in e for e in errors)


class TestResolveOrCreateTargetProfile:
    def _db(self):
        from sqlalchemy.orm import Session

        return MagicMock(spec=Session)

    def test_none_profile_data_returns_none(self):
        from api.services.export import resolve_or_create_target_profile

        assert resolve_or_create_target_profile(None, self._db()) is None

    def test_empty_dict_returns_none(self):
        from api.services.export import resolve_or_create_target_profile

        assert resolve_or_create_target_profile({}, self._db()) is None

    def test_profile_without_name_returns_none(self):
        from api.services.export import resolve_or_create_target_profile

        assert (
            resolve_or_create_target_profile({"total_solids_min": 30}, self._db())
            is None
        )

    def test_existing_profile_returned_without_creating(self):
        from api.models import TargetProfile
        from api.services.export import resolve_or_create_target_profile

        db = self._db()
        existing = MagicMock(spec=TargetProfile)
        db.scalars.return_value.first.return_value = existing

        result = resolve_or_create_target_profile({"name": "Gelato"}, db)

        assert result is existing
        db.add.assert_not_called()

    def test_new_profile_created_when_not_found(self):
        from api.services.export import resolve_or_create_target_profile

        db = self._db()
        db.scalars.return_value.first.return_value = None

        result = resolve_or_create_target_profile(
            {"name": "Sorbet", "total_solids_min": 28.0}, db
        )

        assert result is not None
        db.add.assert_called_once()
        db.flush.assert_called_once()


class TestRoundTrip:
    """Test that recipes can be exported and imported with data integrity."""

    @pytest.mark.integration
    def test_export_import_round_trip_with_target_profile(
        self,
        test_db,
        db_ingredient_factory,
        db_profile_factory,
        db_recipe_factory,
    ):
        """Export a recipe with target profile, import it, verify it's the same."""
        from api.services.export import (
            build_export_single,
            create_recipes_from_import,
        )

        # Create ingredients
        ing1 = db_ingredient_factory(
            name="Sugar",
            water_pct=0.0,
            total_sugar_pct=100.0,
            sucrose_pct=100.0,
        )
        ing2 = db_ingredient_factory(
            name="Water",
            water_pct=100.0,
        )

        # Create target profile
        profile = db_profile_factory(
            name="Test Profile",
            sweetness_min=20.0,
            sweetness_max=35.0,
            total_solids_min=30.0,
            total_solids_max=45.0,
        )

        # Create recipe with target profile and ingredients
        recipe = db_recipe_factory(
            name="Test Recipe",
            description="A test recipe",
            recipe_type="gelato",
            target_profile_id=profile.id,
            ingredients=[
                (ing1, 200.0),
                (ing2, 800.0),
            ],
        )

        # Export the recipe
        export_data = build_export_single(recipe)

        # Verify export has the profile (Pydantic model, use attributes)
        assert export_data.target_profile is not None
        assert export_data.target_profile.name == "Test Profile"
        assert export_data.ingredients
        assert len(export_data.ingredients) == 2

        # Convert to dict for import (model_dump serializes ORM objects)
        export_dict = export_data.model_dump(mode="json")

        # Import the exported data
        imported_recipes = create_recipes_from_import([export_dict], test_db)
        assert len(imported_recipes) == 1

        imported_recipe = imported_recipes[0]

        # Verify the imported recipe matches the original
        assert imported_recipe.name == recipe.name
        assert imported_recipe.description == recipe.description
        assert imported_recipe.recipe_type == recipe.recipe_type
        assert len(imported_recipe.ingredients) == len(recipe.ingredients)
        assert imported_recipe.target_profile is not None
        assert recipe.target_profile is not None
        assert imported_recipe.target_profile.name == recipe.target_profile.name

        # Verify sorted order is preserved
        orig_sorted = sorted(recipe.ingredients, key=lambda x: x.sort_order)
        imported_sorted = sorted(
            imported_recipe.ingredients, key=lambda x: x.sort_order
        )
        for orig, imported in zip(orig_sorted, imported_sorted):
            assert imported.ingredient_id == orig.ingredient_id
            assert imported.weight_grams == orig.weight_grams
            assert imported.sort_order == orig.sort_order

    @pytest.mark.integration
    def test_import_fallback_resolves_stale_uuid_by_source_metadata(
        self,
        test_db,
        db_ingredient_factory,
    ):
        """If ingredient_id is stale, import should resolve by source/source_id."""
        from api.services.export import create_recipes_from_import, validate_import_data

        ingredient = db_ingredient_factory(
            name="Oil, canola, composite",
            source="nzfcdb",
            source_id="J1033",
        )

        recipes_data = [
            {
                "name": "Fallback Import Test",
                "ingredients": [
                    {
                        "ingredient_id": "00000000-0000-0000-0000-000000000123",
                        "weight_grams": 25.0,
                        "sort_order": 0,
                        "ingredient": {
                            "name": "Oil, canola, composite",
                            "source": "nzfcdb",
                            "source_id": "J1033",
                        },
                    }
                ],
            }
        ]

        errors = validate_import_data(recipes_data, test_db)
        assert errors == []

        created = create_recipes_from_import(recipes_data, test_db)
        assert len(created) == 1
        assert len(created[0].ingredients) == 1
        assert created[0].ingredients[0].ingredient_id == ingredient.id
