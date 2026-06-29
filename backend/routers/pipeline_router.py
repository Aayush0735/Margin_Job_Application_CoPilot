"""Pipeline router — trigger AI pipeline, regenerate sections, download artifacts."""
import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from auth import get_current_user
from agents.orchestrator import run_pipeline, run_single_agent
from utils.pdf_parser import parse_pdf
from utils.jd_scraper import scrape_jd
from utils.docx_export import cover_letter_to_docx, resume_to_docx
import models
import schemas

router = APIRouter(tags=["pipeline"])


@router.post("/applications/{app_id}/run-pipeline", response_model=schemas.DraftOut)
async def trigger_pipeline(
    app_id: int,
    resume_file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload resume PDF and run the full multi-agent pipeline."""
    app = _get_app_or_404(db, app_id, current_user.id)

    if app.pipeline_status == "running":
        raise HTTPException(status_code=409, detail="Pipeline already running for this application")

    # Validate file type
    if not resume_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Parse PDF
    pdf_bytes = await resume_file.read()
    if len(pdf_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    try:
        parsed = parse_pdf(pdf_bytes)
        resume_text = parsed["full_text"]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse PDF: {e}")

    if not resume_text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from PDF. Please check the file.")

    # Save resume text to application
    app.original_resume_text = resume_text
    app.original_resume_filename = resume_file.filename
    db.commit()

    # Run pipeline (synchronously here — for production use a task queue)
    try:
        draft = await run_pipeline(db=db, application=app, resume_text=resume_text)
        return schemas.DraftOut.model_validate(draft)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


@router.post("/applications/{app_id}/regenerate/{section}", response_model=schemas.DraftOut)
async def regenerate_section(
    app_id: int,
    section: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Re-run a single agent section without full pipeline rerun."""
    if section not in ("fit", "resume", "cover_letter", "interview"):
        raise HTTPException(status_code=400, detail="section must be: fit, resume, cover_letter, or interview")

    app = _get_app_or_404(db, app_id, current_user.id)

    if not app.original_resume_text:
        raise HTTPException(status_code=400, detail="No resume uploaded yet. Run the full pipeline first.")

    draft = (
        db.query(models.Draft)
        .filter(models.Draft.application_id == app_id)
        .order_by(models.Draft.created_at.desc())
        .first()
    )
    if not draft:
        raise HTTPException(status_code=404, detail="No draft found. Run the full pipeline first.")

    updated_draft = await run_single_agent(
        db=db,
        application=app,
        draft=draft,
        section=section,
        resume_text=app.original_resume_text,
    )
    return schemas.DraftOut.model_validate(updated_draft)


@router.get("/applications/{app_id}/drafts/{draft_id}/download/cover-letter")
def download_cover_letter(
    app_id: int,
    draft_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download cover letter as .docx file."""
    app, draft = _get_draft_or_404(db, app_id, draft_id, current_user.id)

    if not draft.cover_letter:
        raise HTTPException(status_code=404, detail="Cover letter not generated yet")

    docx_bytes = cover_letter_to_docx(
        cover_letter_text=draft.cover_letter,
        applicant_name=current_user.full_name,
        job_title=app.job_title,
        company=app.company,
    )

    filename = f"cover_letter_{app.company}_{app.job_title}.docx".replace(" ", "_")
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/applications/{app_id}/drafts/{draft_id}/download/resume")
def download_resume(
    app_id: int,
    draft_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download rewritten resume as .docx file."""
    app, draft = _get_draft_or_404(db, app_id, draft_id, current_user.id)

    if not draft.resume_rewrite:
        raise HTTPException(status_code=404, detail="Resume rewrite not generated yet")

    docx_bytes = resume_to_docx(
        resume_text=draft.resume_rewrite,
        applicant_name=current_user.full_name,
    )

    filename = f"resume_{app.company}_{app.job_title}.docx".replace(" ", "_")
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/scrape-jd", response_model=schemas.ScrapeResponse)
def scrape_jd_endpoint(
    payload: schemas.ScrapeRequest,
    current_user: models.User = Depends(get_current_user),
):
    """Scrape a job description from a URL."""
    try:
        result = scrape_jd(payload.url)
        if not result.get("jd_text"):
            raise HTTPException(status_code=422, detail="Could not extract JD text from URL")
        return schemas.ScrapeResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── Helpers ──────────────────────────────────────────────────────────────────

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


def _get_draft_or_404(db, app_id, draft_id, user_id):
    app = _get_app_or_404(db, app_id, user_id)
    draft = db.query(models.Draft).filter(
        models.Draft.id == draft_id,
        models.Draft.application_id == app_id,
    ).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return app, draft
