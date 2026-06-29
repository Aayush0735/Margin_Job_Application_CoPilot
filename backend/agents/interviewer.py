"""Agent 4: Interviewer — generates mock interview Q&A grounded in the resume."""
import json
import re
from typing import List, Dict, Any
from groq import Groq
from config import settings

from agents.client_factory import get_client


INTERVIEWER_SYSTEM = """You are a senior hiring manager and interview coach.
Generate exactly 10 likely interview questions for the given role, along with strong sample answers grounded in the candidate's resume.

Question mix:
- 3 behavioural (STAR format, e.g. "Tell me about a time...")
- 3 technical/role-specific (based on JD requirements)
- 2 situational ("How would you handle...")
- 1 motivation ("Why this role/company?")
- 1 weakness/growth area (turn gap into growth story)

Rules for answers:
- Base answers on ACTUAL resume content — specific companies, projects, metrics
- Use STAR format for behavioural questions
- Be concise but substantive (100-200 words per answer)
- Flag which JD skill/requirement each question tests

Return valid JSON only:
{
  "questions": [
    {
      "id": 1,
      "type": "behavioural|technical|situational|motivation|growth",
      "question": "<full question text>",
      "tests": "<JD requirement this tests>",
      "sample_answer": "<strong sample answer grounded in resume>",
      "tips": "<1 tip for delivering this answer well>"
    }
  ]
}"""


async def run_interview_prep(
    resume_text: str,
    jd_text: str,
    job_title: str,
    company: str,
    fit_analysis: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Generate interview Q&A. Returns list of Q&A dicts."""
    client = get_client()

    gaps = [g["skill"] for g in fit_analysis.get("skill_gaps", [])[:3]]
    red_flags = fit_analysis.get("red_flags", [])[:2]

    prompt = f"""CANDIDATE RESUME:
{resume_text[:4000]}

JOB DESCRIPTION:
{jd_text[:3000]}

ROLE: {job_title} at {company}
POTENTIAL SKILL GAPS TO ADDRESS: {', '.join(gaps)}
RED FLAGS TO PREPARE FOR: {'; '.join(red_flags)}

Generate 10 interview questions and strong sample answers. Return JSON only."""

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": INTERVIEWER_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
        max_tokens=settings.llm_max_tokens,
    )

    raw = response.choices[0].message.content.strip()
    result = _parse_json_response(raw)
    return result.get("questions", [])


def _parse_json_response(text: str) -> dict:
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
    return {"questions": []}
