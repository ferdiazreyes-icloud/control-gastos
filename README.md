# Control Gastos

> AI-powered expense tracker that reads Gmail to detect and classify financial movements.

## Status

**Version:** 0.3.0 (Gmail integration — OAuth 2.0 + email fetching)

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

### Pending (MVP — V0)
- [ ] AI analysis engine (Claude API, prompt engineering)
- [ ] Frontend screens (daily review, categories, tags, history)
- [ ] End-to-end flow (Gmail → AI → API → UI)

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
