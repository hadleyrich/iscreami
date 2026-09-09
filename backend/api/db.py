"""Database engine, session factory, and FastAPI dependency."""

from collections.abc import Generator, Mapping
from typing import Annotated, Any

from fastapi import Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from api.settings import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]


def commit_or_conflict(db: Session, message: str) -> None:
    """Commit, translating an IntegrityError (e.g. a FK constraint blocking a
    delete) into a 409 HTTPException. Rolls back so the session stays usable
    after the failed commit."""
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=message) from None


def apply_updates(obj: Any, updates: Mapping[str, Any]) -> None:
    """Apply an ``exclude_unset`` PATCH payload onto an ORM object.

    Shared by the three update endpoints (ingredients/profiles/recipes) so the
    ``for key, value in payload.items(): setattr(obj, key, value)`` loop can't
    drift between them.
    """
    for key, value in updates.items():
        setattr(obj, key, value)


NOT_FOUND_RESPONSE: dict[int | str, dict[str, str]] = {
    404: {"description": "Not found"}
}
