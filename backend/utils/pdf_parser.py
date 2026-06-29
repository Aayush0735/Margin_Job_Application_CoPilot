"""Resume PDF parser using pypdf."""
import io
import re
from typing import Dict, List
import pypdf


def parse_pdf(file_bytes: bytes) -> Dict[str, str]:
    """
    Parse a PDF resume into a dict of sections.
    Returns: {
        'full_text': str,
        'sections': {
            'header': str,
            'summary': str,
            'experience': str,
            'education': str,
            'skills': str,
            'projects': str,
            'certifications': str,
        }
    }
    """
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    pages_text = []
    for page in reader.pages:
        pages_text.append(page.extract_text() or "")

    full_text = "\n".join(pages_text)
    sections = _extract_sections(full_text)

    return {
        "full_text": full_text,
        "sections": sections,
    }


# Common section header patterns
SECTION_PATTERNS = [
    (r"(?i)(summary|objective|profile|about me)", "summary"),
    (r"(?i)(experience|work history|employment|professional experience)", "experience"),
    (r"(?i)(education|academic|qualifications)", "education"),
    (r"(?i)(skills|technical skills|core competencies|technologies)", "skills"),
    (r"(?i)(projects|portfolio|personal projects)", "projects"),
    (r"(?i)(certifications?|licenses?|credentials)", "certifications"),
    (r"(?i)(awards?|achievements?|honors?)", "awards"),
    (r"(?i)(languages?)", "languages"),
]


def _extract_sections(text: str) -> Dict[str, str]:
    """Split resume text into named sections."""
    lines = text.split("\n")
    sections: Dict[str, List[str]] = {"header": []}
    current_section = "header"

    for line in lines:
        matched = False
        for pattern, section_name in SECTION_PATTERNS:
            # Check if line is a section header (short line matching pattern)
            if re.match(pattern, line.strip()) and len(line.strip()) < 60:
                current_section = section_name
                if section_name not in sections:
                    sections[section_name] = []
                matched = True
                break
        if not matched:
            sections.setdefault(current_section, []).append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if v}


def extract_experience_bullets(text: str) -> List[Dict[str, str]]:
    """
    Extract individual bullet points from experience section.
    Returns list of {role_context, bullet} dicts.
    """
    bullets = []
    current_role = "Unknown Role"
    
    # Role title patterns (e.g., "Software Engineer at Google")
    role_pattern = re.compile(
        r"(?i)^(.{10,80}?)\s+(at|@|,|\|)\s+(.{3,50}?)\s*$"
    )
    # Bullet patterns
    bullet_pattern = re.compile(r"^\s*[•\-\*▪◦–]\s+(.+)$")
    
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        role_match = role_pattern.match(line)
        bullet_match = bullet_pattern.match(line)
        
        if role_match:
            current_role = line
        elif bullet_match:
            bullets.append({
                "role_context": current_role,
                "bullet": bullet_match.group(1).strip(),
            })
        elif line and len(line) > 20 and not line[0].isdigit():
            # Non-bullet, non-role descriptive line — treat as implicit bullet
            bullets.append({
                "role_context": current_role,
                "bullet": line,
            })
    
    return bullets
