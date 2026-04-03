# Control Gastos

> AI-powered expense tracker that reads Gmail to detect and classify financial movements.

## Status

**Version:** 1.3.0 (production deploy — Supabase + Railway + Vercel)

### Implemented
- [x] Project setup (repo, template, branch rules)
- [x] Architecture definition (TOGAF ADM artifacts in `.specify/`)
- [x] Version roadmap (`tasks.md`)
- [x] Backend project structure (FastAPI, models, routers, schemas, tests)
- [x] Database schema (movements, categories, tags, processed_emails)
- [x] Frontend project structure (Next.js, PWA manifest, Tailwind CSS)
- [x] Docker Compose for local development (PostgreSQL + backend)
- [x] CI/CD pipeline (GitHub Actions: lint, test, build)
- [x] Makefile with standard commands
- [x] Gmail OAuth 2.0 flow (login, callback, token storage)
- [x] Email fetching service (read emails, skip already processed)
- [x] Auth and email API endpoints
- [x] AI analysis engine (Claude API, prompt engineering, structured extraction)
- [x] Full pipeline: Gmail → AI → store movements as "pending"
- [x] `/api/emails/process` endpoint (fetch + analyze + store in one call)

- [x] Gmail OAuth PKCE fix (validated with real Google auth)
- [x] Initial DB migration (Alembic)
- [x] Integration tested: all APIs validated against real PostgreSQL, Gmail, and Claude API

- [x] Frontend PWA: daily review screen (confirm/edit/discard movements)
- [x] Frontend PWA: history view with filters (confirmed/discarded/all)
- [x] Frontend PWA: category management (create/delete)
- [x] Frontend PWA: tag management (create/delete)
- [x] Frontend PWA: bottom navigation, mobile-first responsive design
- [x] Frontend PWA: edit movement modal (change amount, type, category, tags)

- [x] HTML email cleanup (BeautifulSoup strips HTML → clean text for AI)
- [x] AI response parsing fix (strip markdown code fences from Claude responses)
- [x] End-to-end validated: Gmail → AI → movement appears in app
- [x] Bank email detection validated: Santander, Banamex, Uber, Uber Eats, PayPal (7/7 detected, 0 false positives)
- [x] Sender whitelist: only analyze emails from known financial senders (dynamic, manageable from app)
- [x] Auto-date filter: only fetch emails since last processing run
- [x] Duplicate detection: scoring algorithm (amount + merchant + date + account)
- [x] Pre-auth and progressive email handling (Uber $1 holds, Uber Eats multi-email)
- [x] Duplicate UI: grouped cards with "Conservar este" / "No son duplicados"
- [x] Senders management screen (add/remove sender patterns)
- [x] History: edit movements and change status (confirmed ↔ discarded) with confirmation dialog

- [x] Production deploy: Supabase (DB), Railway (backend), Vercel (frontend)
- [x] Gmail OAuth working in production
- [x] End-to-end validated in production (Gmail → AI → movements in app)

### Pending (next steps)
- [ ] Playwright tests for frontend

### Future Versions
- **V1:** MoneyStats CSV export, AI-suggested categories, recurring movement detection
- **V2:** React Native migration, push notifications, full MoneyStats replacement

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.9+ / FastAPI |
| Frontend | Next.js 14+ / React / TypeScript |
| Database | PostgreSQL (Docker local, Supabase prod) |
| AI | Claude API |
| Hosting | Vercel (frontend) + Railway (backend) |

## Project Structure

```
control-gastos/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routers/         # API endpoints
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── config.py        # Settings from env vars
│   │   ├── database.py      # DB connection
│   │   └── main.py          # FastAPI app
│   ├── alembic/             # DB migrations
│   ├── tests/               # pytest tests
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                # Next.js PWA
│   ├── app/                 # Next.js App Router pages
│   ├── components/          # React components
│   ├── lib/                 # Utilities (API client, etc.)
│   ├── public/              # Static assets + PWA manifest
│   ├── Dockerfile
│   └── package.json
├── .github/workflows/       # CI/CD
├── .specify/                # TOGAF ADM architecture docs
├── docker-compose.yml       # Local dev environment
├── Makefile                 # Standard commands
└── tasks.md                 # Version roadmap
```

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 20+
- Docker & Docker Compose

### Run locally

```bash
# Start backend + database
make up

# In another terminal, start frontend
cd frontend && npm install && npm run dev
```

- Backend API: http://localhost:8000
- API docs (Swagger): http://localhost:8000/docs
- Frontend: http://localhost:3000

### Production URLs

- Frontend: https://control-gastos-six-theta.vercel.app
- Backend API: https://control-gastos-backend-production-b64a.up.railway.app
- Database: Supabase (PostgreSQL) via session pooler

### Run tests

```bash
make test
```

### Other commands

```bash
make down          # Stop all containers
make logs          # View container logs
make lint          # Run linters (ruff + eslint)
make migrate       # Run database migrations
make migration msg="description"  # Create new migration
```

## Architecture

See `.specify/` for full TOGAF ADM documentation:

| File | Description |
|---|---|
| `00-principles.md` | Immutable principles & constraints |
| `01-architecture-vision.md` | Problem, stakeholders, scope |
| `02-business-architecture.md` | User flows, business processes |
| `03-information-systems-architecture.md` | Data model, integrations |
| `04-technology-architecture.md` | Stack, infrastructure |
| `05-opportunities-and-solutions.md` | Technical decisions |
| `requirements.md` | Functional & non-functional requirements |
