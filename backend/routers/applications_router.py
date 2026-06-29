"""Applications CRUD router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from auth import get_current_user
import models
import schemas

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=List[schemas.ApplicationSummary])
def list_applications(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    apps = (
        db.query(models.Application)
        .filter(models.Application.user_id == current_user.id)
        .order_by(models.Application.updated_at.desc())
        .all()
    )
    return [schemas.ApplicationSummary.model_validate(a) for a in apps]


@router.post("", response_model=schemas.ApplicationOut, status_code=201)
def create_application(
    payload: schemas.ApplicationCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app = models.Application(
        user_id=current_user.id,
        job_title=payload.job_title,
        company=payload.company,
        jd_text=payload.jd_text,
        jd_url=payload.jd_url,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return schemas.ApplicationOut.model_validate(app)


@router.get("/{app_id}", response_model=schemas.ApplicationOut)
def get_application(
    app_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app = _get_app_or_404(db, app_id, current_user.id)
    return schemas.ApplicationOut.model_validate(app)


@router.put("/{app_id}", response_model=schemas.ApplicationOut)
def update_application(
    app_id: int,
    payload: schemas.ApplicationUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app = _get_app_or_404(db, app_id, current_user.id)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(app, field, value)
    db.commit()
    db.refresh(app)
    return schemas.ApplicationOut.model_validate(app)


@router.delete("/{app_id}", status_code=204)
def delete_application(
    app_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app = _get_app_or_404(db, app_id, current_user.id)
    db.delete(app)
    db.commit()


@router.get("/{app_id}/drafts", response_model=List[schemas.DraftOut])
def list_drafts(
    app_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_app_or_404(db, app_id, current_user.id)
    drafts = (
        db.query(models.Draft)
        .filter(models.Draft.application_id == app_id)
        .order_by(models.Draft.created_at.desc())
        .all()
    )
    return [schemas.DraftOut.model_validate(d) for d in drafts]


@router.get("/{app_id}/drafts/latest", response_model=schemas.DraftOut)
def get_latest_draft(
    app_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_app_or_404(db, app_id, current_user.id)
    draft = (
        db.query(models.Draft)
        .filter(models.Draft.application_id == app_id)
        .order_by(models.Draft.created_at.desc())
        .first()
    )
    if not draft:
        raise HTTPException(status_code=404, detail="No drafts yet")
    return schemas.DraftOut.model_validate(draft)


# ── Helper ───────────────────────────────────────────────────────────────────

def _get_app_or_404(db: Session, app_id: int, user_id: int) -> models.Application:
    app = (
        db.query(models.Application)
        .filter(
            models.Application.id == app_id,
            models.Application.user_id == user_id,
        )
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app
