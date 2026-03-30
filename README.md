# Control Gastos

> AI-powered expense tracker that reads Gmail to detect and classify financial movements.

## Status

**Version:** 0.1.0 (project setup — architecture defined, no code yet)

### Implemented
- [x] Project setup (repo, template, branch rules)
- [x] Architecture definition (TOGAF ADM artifacts in `.specify/`)
- [x] Version roadmap (`tasks.md`)

### Pending (MVP — V0)
- [ ] Backend project structure (FastAPI + Docker)
- [ ] Database schema and migrations (Supabase/PostgreSQL)
- [ ] Gmail API integration (OAuth 2.0, email fetching)
- [ ] AI analysis engine (Claude API, prompt engineering)
- [ ] REST API for movements, categories, tags
- [ ] Frontend PWA (Next.js, mobile-first)
- [ ] Daily movement review flow (confirm/edit/discard)

### Future Versions
- **V1:** MoneyStats CSV export, AI-suggested categories, recurring movement detection
- **V2:** React Native migration, push notifications, full MoneyStats replacement

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12+ / FastAPI |
| Frontend | Next.js 14+ / React / TypeScript |
| Database | PostgreSQL via Supabase |
| AI | Claude API |
| Hosting | Vercel (frontend) + Railway (backend) |

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- Gmail account with API access (Google Cloud project)
- Claude API key (Anthropic)
- Supabase project (free tier)

### Run locally
```bash
make up
```

### Run tests
```bash
make test
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
