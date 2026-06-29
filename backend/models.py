"""SQLAlchemy ORM models."""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class ApplicationStatus(str, enum.Enum):
    NOT_YET = "not_yet"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    jd_text = Column(Text, nullable=False)
    jd_url = Column(String(1000), nullable=True)
    status = Column(
        Enum(ApplicationStatus),
        default=ApplicationStatus.NOT_YET,
        nullable=False
    )
    original_resume_text = Column(Text, nullable=True)
    original_resume_filename = Column(String(255), nullable=True)
    pipeline_status = Column(String(50), default="pending")  # pending, running, done, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="applications")
    drafts = relationship("Draft", back_populates="application", cascade="all, delete-orphan", order_by="Draft.created_at.desc()")


class Draft(Base):
    __tablename__ = "drafts"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    fit_analysis = Column(JSON, nullable=True)       # {matched: [...], gaps: [...], score: int, emphasis: [...]}
    resume_rewrite = Column(Text, nullable=True)
    cover_letter = Column(Text, nullable=True)
    interview_qa = Column(JSON, nullable=True)       # [{question: str, answer: str}, ...]
    ats_score = Column(Integer, nullable=True)        # 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    application = relationship("Application", back_populates="drafts")
    resume_sections = relationship("ResumeSection", back_populates="draft", cascade="all, delete-orphan")


class ResumeSection(Base):
    __tablename__ = "resume_sections"

    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("drafts.id", ondelete="CASCADE"), nullable=False)
    section_name = Column(String(100), nullable=False)   # e.g. "Experience - Software Engineer at Acme"
    original_text = Column(Text, nullable=False)
    rewritten_text = Column(Text, nullable=False)

    draft = relationship("Draft", back_populates="resume_sections")
