"""Tests for recipe API routes."""

from __future__ import annotations

import asyncio
import io
from unittest.mock import MagicMock

import pytest
from starlette.datastructures import UploadFile

from api.routes.recipes import import_recipes


class TestImportRecipes:
    """Tests for POST /recipes/import."""

    def test_none_size_rejected(self):
        """UploadFile with size=None should return 400.

        When UploadFile.size is None (possible with chunked transfer
        encoding or missing Content-Length header), the handler must
        reject the request before attempting to read the file.
        """
        file = UploadFile(
            file=io.BytesIO(b"{}"),
            size=None,
            filename="test.json",
        )
        db = MagicMock()

        with pytest.raises(Exception) as exc_info:
            asyncio.run(import_recipes(file=file, db=db))

        assert exc_info.value.status_code == 400  # type: ignore[union-attr]
        assert (
            "size could not be determined" in exc_info.value.detail.lower()  # type: ignore[union-attr]
        )
