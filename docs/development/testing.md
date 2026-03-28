# Testing Guide

## Overview

The iscreami backend uses `pytest` with coverage reporting. Tests are organized by type (unit, integration) using markers for easy filtering.

**Current Coverage:**
- Services: 98%+ (calculator, export, composition, etc.)
- Schemas: 98%+ (request/response validation)
- Routes: Not yet tested (0%) — use integration/e2e tests when added

## Running Tests

### All tests
```bash
uv run pytest tests/ -v
```

### Unit tests only (fast)
```bash
uv run pytest tests/ -m "not integration" -v
```

### Integration tests only
```bash
uv run pytest tests/ -m integration -v
```

### Specific test file
```bash
uv run pytest tests/test_calculator.py -v
```

### Specific test class or function
```bash
uv run pytest tests/test_calculator.py::TestPAC::test_sodium_contributes_to_pac -v
```

## Coverage Reports

After running tests, coverage reports are automatically generated:

1. **Terminal summary** — shown in pytest output
2. **HTML report** — open `htmlcov/index.html` in a browser for detailed line-by-line coverage

```bash
# Run tests and generate coverage
uv run pytest tests/

# Open coverage report
open htmlcov/index.html    # macOS
xdg-open htmlcov/index.html # Linux
start htmlcov/index.html   # Windows
```

### Coverage configuration
Coverage settings are in `pyproject.toml`:

- **Branch coverage** enabled (`--cov-branch`)
- **Missing lines** shown in terminal (`--cov-report=term-missing`)
- **HTML output** to `htmlcov/` directory
- **Excluded patterns** for abstract methods, type checking code, etc.

## Test Organization

### Unit Tests (Mocked Dependencies)
For testing business logic without external dependencies.

**Characteristics:**
- Fast (<100ms per test)
- No database queries
- Mock external services
- Use `ingredient` and `profile` fixtures for mock factories

**Example:**
```python
def test_pac_calculation(ingredient):
    mock_ing = ingredient(water_pct=10, sucrose_pct=20)
    result = ingredient_pac(mock_ing)
    assert result > 0
```

**Run with:** `pytest -m "not integration"`

### Integration Tests (Real Database)
For testing workflows that require actual ORM/database interaction.

**Characteristics:**
- Slightly slower (50-200ms per test)
- Use real SQLite in-memory database
- Test full feature workflows (e.g., export → import round-trip)
- Use `test_db` and factory fixtures (`db_ingredient_factory`, `db_profile_factory`, `db_recipe_factory`)

**Example:**
```python
@pytest.mark.integration
def test_export_import_round_trip(test_db, db_recipe_factory):
    recipe = db_recipe_factory(name="Gelato")
    export_data = build_export_single(recipe)
    # ... test export/import cycle
```

**Run with:** `pytest -m integration`

## Database Fixtures

For integration tests, use the factory fixtures in `conftest.py`:

### `test_db`
Fresh in-memory SQLite database for each test function.

```python
def test_something(test_db):
    # Use test_db directly
    from sqlalchemy.orm import Session
    assert isinstance(test_db, Session)
```

### `db_ingredient_factory`
Create real `Ingredient` ORM objects.

```python
def test_with_ingredient(test_db, db_ingredient_factory):
    ing = db_ingredient_factory(
        name="Sugar",
        water_pct=0.0,
        total_sugar_pct=100.0,
    )
    assert ing.id is not None
```

### `db_profile_factory`
Create real `TargetProfile` ORM objects.

```python
def test_with_profile(test_db, db_profile_factory):
    profile = db_profile_factory(
        name="Gelato",
        sweetness_min=20.0,
        sweetness_max=35.0,
    )
    assert profile.id is not None
```

### `db_recipe_factory`
Create real `Recipe` ORM objects with ingredients.

```python
def test_with_recipe(test_db, db_recipe_factory, db_ingredient_factory):
    ing1 = db_ingredient_factory(name="Sugar")
    ing2 = db_ingredient_factory(name="Water")
    
    recipe = db_recipe_factory(
        name="Test Recipe",
        ingredients=[
            (ing1, 200.0),  # (ingredient, weight_grams)
            (ing2, 800.0),
        ],
    )
    assert len(recipe.ingredients) == 2
```

## Mock Fixtures

For unit tests, use mock factories:

### `ingredient`
Mock factory for Ingredient objects.

```python
def test_calculation(ingredient):
    mock_ing = ingredient(
        name="Water",
        water_pct=100.0,
        total_sugar_pct=None,
    )
    # Mock object with specified properties
    assert mock_ing.water_pct == 100.0
```

### `profile`
Mock factory for TargetProfile objects.

```python
def test_with_profile(profile):
    mock_profile = profile(
        sweetness_min=20.0,
        sweetness_max=35.0,
    )
    assert mock_profile.sweetness_min == 20.0
```

## Best Practices

1. **Prefer unit tests** — they're fast and isolated. Use integration tests only for workflows that truly need the ORM.

2. **Clear test names** — use descriptive names that explain what is being tested:
   ```python
   # Good
   def test_sodium_mg_added_to_pac_calculation
   
   # Bad
   def test_pac
   ```

3. **One assertion per test** (when possible) — makes failures clear. Multiple related assertions are OK.

4. **Arrange-Act-Assert pattern**:
   ```python
   def test_something(ingredient):
       # Arrange
       mock_ing = ingredient(water_pct=10)
       
       # Act
       result = some_function(mock_ing)
       
       # Assert
       assert result == expected
   ```

5. **Use factories for complex objects** — don't repeat setup code:
   ```python
   # Bad: repeated across tests
   recipe = Recipe(name="Test", ...)
   db.add(recipe)
   
   # Good: use factory
   recipe = db_recipe_factory(name="Test")
   ```

6. **Mark integration tests** — use `@pytest.mark.integration` so you can filter them:
   ```python
   @pytest.mark.integration
   def test_export_import_workflow(test_db):
       ...
   ```

## Continuous Integration

For CI/CD, consider running:

```bash
# Fast: unit tests only (commit checks)
uv run pytest tests/ -m "not integration" -q

# Full: all tests with coverage (pre-merge)
uv run pytest tests/ -q --cov-report=term-missing:skip-covered
```

## Troubleshooting

### Import errors in tests
Ensure `__init__.py` files exist in test directories or configure `pythonpath` in `pyproject.toml`.

### Fixture not found errors
Check that fixtures are defined in `conftest.py` or imported correctly.

### Coverage not generated
Coverage requires `pytest-cov` to be installed:
```bash
uv sync  # Re-install from pyproject.toml
```

### View HTML coverage details
The HTML report shows:
- Per-file coverage percentages
- Uncovered lines highlighted in red
- Branch coverage (decisions not taken)
- Partial branch coverage (one path taken)

Click on a file to see line-by-line details.
