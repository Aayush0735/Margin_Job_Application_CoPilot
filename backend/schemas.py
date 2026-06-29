"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Any
from datetime import datetime
from models import ApplicationStatus


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ─── Applications ────────────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    job_title: str
    company: str
    jd_text: str
    jd_url: Optional[str] = None


class ApplicationUpdate(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    jd_text: Optional[str] = None
    jd_url: Optional[str] = None
    status: Optional[ApplicationStatus] = None


class ApplicationOut(BaseModel):
    id: int
    job_title: str
    company: str
    jd_text: str
    jd_url: Optional[str]
    status: ApplicationStatus
    original_resume_text: Optional[str]
    original_resume_filename: Optional[str]
    pipeline_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationSummary(BaseModel):
    id: int
    job_title: str
    company: str
    status: ApplicationStatus
    pipeline_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Drafts ──────────────────────────────────────────────────────────────────

class ResumeSectionOut(BaseModel):
    id: int
    section_name: str
    original_text: str
    rewritten_text: str

    model_config = {"from_attributes": True}


class DraftOut(BaseModel):
    id: int
    application_id: int
    fit_analysis: Optional[Any]
    resume_rewrite: Optional[str]
    cover_letter: Optional[str]
    interview_qa: Optional[Any]
    ats_score: Optional[int]
    created_at: datetime
    resume_sections: List[ResumeSectionOut] = []

    model_config = {"from_attributes": True}


# ─── Pipeline ────────────────────────────────────────────────────────────────

class PipelineRequest(BaseModel):
    section: Optional[str] = None  # for regenerate: fit|resume|cover_letter|interview


class ScrapeRequest(BaseModel):
    url: str


class ScrapeResponse(BaseModel):
    jd_text: str
    title: Optional[str] = None
    company: Optional[str] = None
