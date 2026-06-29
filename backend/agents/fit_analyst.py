"""Agent 1: Fit Analyst — analyses resume vs job description."""
import json
import re
from typing import Dict, Any
from groq import Groq
from config import settings

from agents.client_factory import get_client


FIT_ANALYST_SYSTEM = """You are an expert career coach and ATS specialist. Your job is to analyse a candidate's resume against a job description and produce a structured fit analysis.

You MUST respond with a valid JSON object only. No markdown, no prose outside JSON.

JSON schema:
{
  "overall_score": <integer 0-100>,
  "match_summary": "<2-3 sentence summary>",
  "matched_skills": [
    {"skill": "<skill>", "evidence": "<where in resume>", "importance": "high|medium|low"}
  ],
  "skill_gaps": [
    {"skill": "<missing skill>", "importance": "high|medium|low", "suggestion": "<how to address>"}
  ],
  "emphasis_points": ["<what to highlight in application>"],
  "keywords_to_add": ["<JD keyword missing from resume>"],
  "red_flags": ["<potential concerns>"]
}"""


async def run_fit_analysis(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """Run fit analysis agent. Returns parsed JSON dict."""
    client = get_client()

    prompt = f"""RESUME:
{resume_text[:6000]}

JOB DESCRIPTION:
{jd_text[:4000]}

Analyse the fit between this resume and job description. Return JSON only."""

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": FIT_ANALYST_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()
    return _parse_json_response(raw, default_fit_analysis())


def default_fit_analysis() -> Dict[str, Any]:
    return {
        "overall_score": 0,
        "match_summary": "Analysis unavailable.",
        "matched_skills": [],
        "skill_gaps": [],
        "emphasis_points": [],
        "keywords_to_add": [],
        "red_flags": [],
    }


def _parse_json_response(text: str, default: dict) -> dict:
    """Safely parse JSON from LLM response."""
    # Strip markdown code blocks if present
    text = re.sub(r"```(?:json)?\n?", "", text).strip().rstrip("`")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return default
