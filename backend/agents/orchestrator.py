"""
Multi-agent orchestrator — hand-rolled coordinator pattern.

Pipeline:
  1. Agent 1 (Fit Analyst) runs first — its output feeds agents 2, 3, 4
  2. Agents 2, 3, 4 run in parallel (asyncio.gather)
  3. Results are persisted to DB
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from agents.fit_analyst import run_fit_analysis
from agents.resume_writer import run_resume_rewrite
from agents.cover_letter import run_cover_letter
from agents.interviewer import run_interview_prep
import models

logger = logging.getLogger(__name__)


async def run_pipeline(
    db: Session,
    application: models.Application,
    resume_text: str,
) -> models.Draft:
    """
    Run the full 4-agent pipeline for a given application.
    Updates application.pipeline_status and creates a Draft record.
    """
    app_id = application.id
    job_title = application.job_title
    company = application.company
    jd_text = application.jd_text
    applicant_name = application.user.full_name if application.user else ""

    # Mark as running
    _update_pipeline_status(db, application, "running")

    try:
        # ── Stage 1: Fit Analysis ──────────────────────────────────────────
        logger.info(f"[App {app_id}] Running fit analyst...")
        fit_analysis = await run_fit_analysis(resume_text, jd_text)
        logger.info(f"[App {app_id}] Fit score: {fit_analysis.get('overall_score')}")

        # ── Stage 2: Parallel agents ───────────────────────────────────────
        logger.info(f"[App {app_id}] Running resume writer, cover letter, interviewer in parallel...")
        resume_result, cover_letter_text, interview_qa = await asyncio.gather(
            run_resume_rewrite(resume_text, jd_text, fit_analysis),
            run_cover_letter(resume_text, jd_text, job_title, company, fit_analysis, applicant_name),
            run_interview_prep(resume_text, jd_text, job_title, company, fit_analysis),
        )
        logger.info(f"[App {app_id}] All agents completed.")

        # ── Stage 3: Persist ───────────────────────────────────────────────
        draft = _save_draft(
            db=db,
            application=application,
            fit_analysis=fit_analysis,
            resume_result=resume_result,
            cover_letter_text=cover_letter_text,
            interview_qa=interview_qa,
        )

        _update_pipeline_status(db, application, "done")
        logger.info(f"[App {app_id}] Pipeline complete. Draft ID: {draft.id}")
        return draft

    except Exception as e:
        logger.error(f"[App {app_id}] Pipeline failed: {e}", exc_info=True)
        _update_pipeline_status(db, application, "failed")
        raise


async def run_single_agent(
    db: Session,
    application: models.Application,
    draft: models.Draft,
    section: str,
    resume_text: str,
) -> models.Draft:
    """
    Regenerate a single section without re-running the full pipeline.
    section: 'fit' | 'resume' | 'cover_letter' | 'interview'
    """
    jd_text = application.jd_text
    job_title = application.job_title
    company = application.company
    applicant_name = application.user.full_name if application.user else ""
    fit_analysis = draft.fit_analysis or {}

    if section == "fit":
        result = await run_fit_analysis(resume_text, jd_text)
        draft.fit_analysis = result

    elif section == "resume":
        result = await run_resume_rewrite(resume_text, jd_text, fit_analysis)
        draft.resume_rewrite = result.get("full_rewrite", draft.resume_rewrite)
        _update_resume_sections(db, draft, result.get("sections", []))

    elif section == "cover_letter":
        result = await run_cover_letter(
            resume_text, jd_text, job_title, company, fit_analysis, applicant_name
        )
        draft.cover_letter = result

    elif section == "interview":
        result = await run_interview_prep(resume_text, jd_text, job_title, company, fit_analysis)
        draft.interview_qa = result

    else:
        raise ValueError(f"Unknown section: {section}")

    db.commit()
    db.refresh(draft)
    return draft


# ── Helpers ──────────────────────────────────────────────────────────────────

def _update_pipeline_status(db: Session, application: models.Application, status: str):
    application.pipeline_status = status
    db.commit()


def _save_draft(
    db: Session,
    application: models.Application,
    fit_analysis: Dict[str, Any],
    resume_result: Dict[str, Any],
    cover_letter_text: str,
    interview_qa: list,
) -> models.Draft:
    draft = models.Draft(
        application_id=application.id,
        fit_analysis=fit_analysis,
        resume_rewrite=resume_result.get("full_rewrite", ""),
        cover_letter=cover_letter_text,
        interview_qa=interview_qa,
        ats_score=fit_analysis.get("overall_score"),
    )
    db.add(draft)
    db.flush()  # Get draft.id

    # Save section diffs
    sections = resume_result.get("sections", [])
    _update_resume_sections(db, draft, sections)

    db.commit()
    db.refresh(draft)
    return draft


def _update_resume_sections(db: Session, draft: models.Draft, sections: list):
    # Clear old sections
    for s in draft.resume_sections:
        db.delete(s)
    db.flush()

    for sec in sections:
        if not sec.get("original") or not sec.get("rewritten"):
            continue
        rs = models.ResumeSection(
            draft_id=draft.id,
            section_name=sec.get("section_name", "Section"),
            original_text=sec["original"],
            rewritten_text=sec["rewritten"],
        )
        db.add(rs)
