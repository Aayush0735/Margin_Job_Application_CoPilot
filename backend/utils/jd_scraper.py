"""Job description scraper using requests + BeautifulSoup."""
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def scrape_jd(url: str) -> Dict[str, Optional[str]]:
    """
    Scrape a job description from a URL.
    Returns {jd_text, title, company}
    """
    url = url.strip()

    if "linkedin.com" in url:
        return _scrape_linkedin(url)
    else:
        return _scrape_generic(url)


def _scrape_linkedin(url: str) -> Dict[str, Optional[str]]:
    """Scrape LinkedIn job posting."""
    # Convert to public view if needed
    if "/jobs/view/" in url and "linkedin.com/jobs/view/" not in url:
        pass

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Job title
        title = None
        title_el = soup.find("h1", class_=re.compile(r"top-card|job-title", re.I))
        if not title_el:
            title_el = soup.find("h1")
        if title_el:
            title = title_el.get_text(strip=True)

        # Company
        company = None
        company_el = soup.find(class_=re.compile(r"company|topcard__org", re.I))
        if company_el:
            company = company_el.get_text(strip=True)

        # JD text
        jd_el = soup.find("div", class_=re.compile(r"description|job-description", re.I))
        if not jd_el:
            jd_el = soup.find("section", class_=re.compile(r"description", re.I))
        
        jd_text = ""
        if jd_el:
            jd_text = jd_el.get_text(separator="\n", strip=True)
        else:
            # Fallback: extract all text from main/article
            main = soup.find("main") or soup.find("article") or soup.body
            if main:
                jd_text = main.get_text(separator="\n", strip=True)

        return {
            "jd_text": _clean_text(jd_text),
            "title": title,
            "company": company,
        }
    except Exception as e:
        raise ValueError(f"Failed to scrape LinkedIn URL: {e}")


def _scrape_generic(url: str) -> Dict[str, Optional[str]]:
    """Generic job page scraper."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove scripts, styles, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Title
        title = None
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title.get("content")
        elif soup.title:
            title = soup.title.get_text(strip=True)

        # Try to find job-specific content div
        content_el = (
            soup.find(id=re.compile(r"job|description|content", re.I))
            or soup.find(class_=re.compile(r"job|description|content|posting", re.I))
            or soup.find("main")
            or soup.body
        )

        jd_text = content_el.get_text(separator="\n", strip=True) if content_el else ""

        return {
            "jd_text": _clean_text(jd_text),
            "title": title,
            "company": None,
        }
    except Exception as e:
        raise ValueError(f"Failed to scrape URL: {e}")


def _clean_text(text: str) -> str:
    """Remove excessive whitespace and noise from scraped text."""
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove lines that are just symbols or very short
    lines = [l for l in text.split("\n") if len(l.strip()) > 2]
    return "\n".join(lines).strip()
