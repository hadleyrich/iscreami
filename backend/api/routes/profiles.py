"""Target profile routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from api.db import NOT_FOUND_RESPONSE, DbSession, apply_updates, commit_or_conflict
from api.models import TargetProfile
from api.schemas import TargetProfileCreate, TargetProfileOut, TargetProfileUpdate

router = APIRouter(prefix="/target-profiles", tags=["target-profiles"])


@router.get("", response_model=list[TargetProfileOut])
def list_profiles(db: DbSession):
    return db.scalars(select(TargetProfile).order_by(TargetProfile.name)).all()


@router.get(
    "/{profile_id}", response_model=TargetProfileOut, responses=NOT_FOUND_RESPONSE
)
def get_profile(profile_id: uuid.UUID, db: DbSession):
    profile = db.get(TargetProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Target profile not found")
    return profile


@router.post("", response_model=TargetProfileOut, status_code=201)
def create_profile(data: TargetProfileCreate, db: DbSession):
    profile = TargetProfile(**data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.put(
    "/{profile_id}", response_model=TargetProfileOut, responses=NOT_FOUND_RESPONSE
)
def update_profile(profile_id: uuid.UUID, data: TargetProfileUpdate, db: DbSession):
    profile = db.get(TargetProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Target profile not found")
    apply_updates(profile, data.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/{profile_id}", status_code=204, responses=NOT_FOUND_RESPONSE)
def delete_profile(profile_id: uuid.UUID, db: DbSession):
    profile = db.get(TargetProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Target profile not found")
    db.delete(profile)
    commit_or_conflict(
        db, "Profile is used in one or more recipes and cannot be deleted"
    )
