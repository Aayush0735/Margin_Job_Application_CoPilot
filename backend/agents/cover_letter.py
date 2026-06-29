"""Agent 3: Cover Letter Writer — crafts a tailored 1-page cover letter."""
import json
import re
from typing import Dict, Any
from groq import Groq
from config import settings

from agents.client_factory import get_client


COVER_LETTER_SYSTEM = """You are an expert cover letter writer with 15 years of hiring experience.
Write a compelling, personalised cover letter for a job application.

Rules:
- Exactly 3-4 paragraphs, maximum 1 page
- Opening: hook with specific enthusiasm for THIS role/company
- Body: connect 2-3 strongest relevant experiences to JD requirements
- Body: address any skill gaps proactively and positively
- Closing: clear call to action, confident tone
- Tone: professional but warm, NOT generic or template-like
- Do NOT use phrases like "I am writing to express my interest" — be direct and engaging
- Ground every claim in the candidate's actual resume

Return plain text cover letter only (no JSON, no markdown headers)."""


async def run_cover_letter(
    resume_text: str,
    jd_text: str,
    job_title: str,
    company: str,
    fit_analysis: Dict[str, Any],
    applicant_name: str = "",
) -> str:
    """Generate cover letter. Returns plain text string."""
    client = get_client()

    matched = [s["skill"] for s in fit_analysis.get("matched_skills", [])[:5]]
    emphasis = fit_analysis.get("emphasis_points", [])[:3]

    prompt = f"""CANDIDATE NAME: {applicant_name or "The Candidate"}

CANDIDATE RESUME:
{resume_text[:4000]}

JOB DESCRIPTION:
{jd_text[:3000]}

ROLE: {job_title} at {company}
STRONGEST MATCHES: {', '.join(matched)}
KEY EMPHASIS POINTS: {'; '.join(emphasis)}

Write a powerful, personalised cover letter for this specific role."""

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": COVER_LETTER_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1200,
    )

    return response.choices[0].message.content.strip()
