"""Agent 2: Resume Writer — rewrites resume bullets tailored to JD."""
import json
import re
from typing import Dict, Any, List
from groq import Groq
from config import settings

from agents.client_factory import get_client


RESUME_WRITER_SYSTEM = """You are an expert resume writer and ATS optimisation specialist. 
Your task is to rewrite a candidate's resume to better match a specific job description.

Rules:
- Keep ALL the same jobs, dates, companies, and education — do NOT invent experience
- Sharpen bullet points with strong action verbs and quantified impact where possible
- Weave in JD keywords naturally — don't keyword-stuff
- Maintain truthfulness — only improve how existing experience is expressed
- Return the FULL rewritten resume text, preserving structure

Also return section-by-section diff data.

You MUST respond with valid JSON only:
{
  "full_rewrite": "<full rewritten resume as text>",
  "sections": [
    {
      "section_name": "<e.g. 'Software Engineer at Acme Corp'>",
      "original": "<original bullet points for this section>",
      "rewritten": "<rewritten bullet points for this section>"
    }
  ],
  "changes_summary": "<brief summary of changes made>"
}"""


async def run_resume_rewrite(
    resume_text: str,
    jd_text: str,
    fit_analysis: Dict[str, Any],
) -> Dict[str, Any]:
    """Rewrite resume tailored to JD, guided by fit analysis."""
    client = get_client()

    keywords = fit_analysis.get("keywords_to_add", [])
    emphasis = fit_analysis.get("emphasis_points", [])

    prompt = f"""ORIGINAL RESUME:
{resume_text[:5000]}

JOB DESCRIPTION:
{jd_text[:3000]}

KEYWORDS TO WEAVE IN: {', '.join(keywords[:15])}
POINTS TO EMPHASISE: {'; '.join(emphasis[:5])}

Rewrite the resume to be highly targeted for this role. Return JSON only."""

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": RESUME_WRITER_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=settings.llm_max_tokens,
    )

    raw = response.choices[0].message.content.strip()
    return _parse_json_response(raw, default_resume_result(resume_text))


def default_resume_result(original: str) -> Dict[str, Any]:
    return {
        "full_rewrite": original,
        "sections": [],
        "changes_summary": "Resume rewrite unavailable.",
    }


def _parse_json_response(text: str, default: dict) -> dict:
    text = re.sub(r"```(?:json)?\n?", "", text).strip().rstrip("`")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return default
