# Margin

> A multi-agent AI system that turns your resume + a job description into a complete, tailored application kit — fit analysis, resume rewrite, cover letter, and mock interview Q&A.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![LLM](https://img.shields.io/badge/Groq-llama--3.3--70b-orange)
![DB](https://img.shields.io/badge/SQLite-SQLAlchemy-blue)
![Frontend](https://img.shields.io/badge/Vanilla-HTML%20%2B%20CSS%20%2B%20JS-yellow)

---

## Features

| Feature | Description |
|---|---|
| **Fit Analysis** | ATS match score, matched skills, gaps, keywords to add |
| **Resume Rewrite** | Tailored bullets with JD keywords, side-by-side diff view |
| **Cover Letter** | 1-page, tone-matched, grounded in real experience, download as .docx |
| **Interview Prep** | 10 Q&A (behavioural, technical, situational) with STAR answers |
| **Regenerate** | Re-run any single agent section independently |
| **JD Scraping** | Paste LinkedIn URL → auto-extract job description |
| **Pipeline Dashboard** | Track all roles: Not Applied → Applied → Interviewing → Offered |
| **JWT Auth** | Secure multi-user support |

---

## Architecture

```
frontend/               ← Vanilla HTML + CSS + JS
  index.html            ← Landing + Auth
  dashboard.html        ← Role pipeline dashboard
  application.html      ← Single role view with AI results

backend/
  main.py               ← FastAPI app
  agents/
    orchestrator.py     ← Multi-agent coordinator
    fit_analyst.py      ← Agent 1: Fit analysis
    resume_writer.py    ← Agent 2: Resume rewrite
    cover_letter.py     ← Agent 3: Cover letter
    interviewer.py      ← Agent 4: Interview Q&A
  routers/              ← API endpoints
  utils/                ← PDF parser, JD scraper, DOCX export
```

### Multi-Agent Pipeline

```
Upload Resume + JD
      ↓
  Orchestrator
      ↓
  Agent 1: Fit Analyst  ← runs first, feeds others
      ↓
  ┌───────────────────────────────┐
  │ Agent 2: Resume Writer        │  ← parallel
  │ Agent 3: Cover Letter Writer  │  ← parallel
  │ Agent 4: Interviewer          │  ← parallel
  └───────────────────────────────┘
      ↓
  Save to SQLite + Return to Frontend
```

---

## Quick Start

### 1. Clone & Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment
copy .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 2. Get a Groq API Key (Free)

1. Visit [console.groq.com](https://console.groq.com)
2. Create a free account
3. Generate an API key
4. Add it to `backend/.env`:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```

### 3. Run the Backend

```bash
cd backend
python main.py
# OR
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`
Interactive docs: `http://localhost:8000/api/docs`

### 4. Open the Frontend

Option A — served by FastAPI (recommended):
```
http://localhost:8000/
```

Option B — open directly in browser:
```
frontend/index.html
```

> **Note:** If opening directly via `file://`, you may need a local dev server to avoid CORS issues with ES modules:
> ```bash
> cd frontend
> python -m http.server 3000
> # Then open http://localhost:3000
> ```

---

## Project Structure

```
Applify/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Settings (env vars)
│   ├── database.py          # SQLAlchemy engine
│   ├── models.py            # ORM models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # JWT utilities
│   ├── agents/
│   │   ├── orchestrator.py  # Coordinator
│   │   ├── fit_analyst.py   # Agent 1
│   │   ├── resume_writer.py # Agent 2
│   │   ├── cover_letter.py  # Agent 3
│   │   └── interviewer.py   # Agent 4
│   ├── routers/
│   │   ├── auth_router.py
│   │   ├── applications_router.py
│   │   └── pipeline_router.py
│   ├── utils/
│   │   ├── pdf_parser.py    # pypdf
│   │   ├── jd_scraper.py    # requests + bs4
│   │   └── docx_export.py   # python-docx
│   ├── requirements.txt
│   └── .env.example
│
├── docs/
│   └── Margin_Presentation.pptx # Pitch deck / Presentation
│
├── frontend/
│   ├── index.html           # Landing + auth
│   ├── dashboard.html       # Role pipeline
│   ├── application.html     # Single role + AI results
│   └── assets/
│       ├── css/
│       │   ├── main.css     # Design system
│       │   └── components.css
│       └── js/
│           ├── api.js       # fetch() + JWT
│           ├── auth.js      # Login/register
│           ├── dashboard.js
│           ├── application.js
│           ├── diff.js      # Resume diff view
│           └── toast.js     # Notifications
│
└── scripts/
    ├── cache_buster.py      # Utility scripts
    └── ... (other maintenance scripts)
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login → JWT token |
| GET  | `/api/auth/me` | Current user |
| GET  | `/api/applications` | List all applications |
| POST | `/api/applications` | Create application |
| GET  | `/api/applications/{id}` | Get single application |
| PUT  | `/api/applications/{id}` | Update (status etc.) |
| DELETE | `/api/applications/{id}` | Delete |
| GET  | `/api/applications/{id}/drafts/latest` | Get latest draft |
| POST | `/api/applications/{id}/run-pipeline` | Run AI pipeline (upload PDF) |
| POST | `/api/applications/{id}/regenerate/{section}` | Re-run one agent |
| GET  | `/api/applications/{id}/drafts/{draftId}/download/cover-letter` | .docx download |
| GET  | `/api/applications/{id}/drafts/{draftId}/download/resume` | .docx download |
| POST | `/api/scrape-jd` | Scrape JD from URL |

Full interactive docs: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vanilla HTML5, CSS3, ES6 Modules |
| Backend | FastAPI (Python 3.11+) |
| AI Pipeline | Hand-rolled coordinator (asyncio.gather) |
| LLM | Groq API — llama-3.3-70b-versatile |
| Database | SQLite + SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| PDF Parse | pypdf |
| JD Scrape | requests + beautifulsoup4 |
| DOCX Export | python-docx |

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `GROQ_API_KEY` | Groq API key (required for AI) | — |
| `SECRET_KEY` | JWT signing secret | change_me |
| `DATABASE_URL` | SQLite URL | `sqlite:///./job_Applify.db` |
| `LLM_MODEL` | Groq model name | `llama-3.3-70b-versatile` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL | 10080 (7 days) |

---

## Testing the API

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","full_name":"Test User","password":"testpass"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}'

# Create Application (use token from login)
curl -X POST http://localhost:8000/api/applications \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"job_title":"Software Engineer","company":"Acme Corp","jd_text":"We are looking for..."}'
```

---

## Development Notes

- The AI pipeline runs **synchronously** in the request. For production, consider Celery + Redis for background task queueing.
- SQLite is used for simplicity. For production, swap to PostgreSQL by changing `DATABASE_URL`.
- CORS is set to `*` for development. Lock it down in production.
- The frontend uses **ES modules** (`type="module"`) — serve via a local server, not `file://`.

---

## License

MIT — build and sell freely.
