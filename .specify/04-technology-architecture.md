# 04 — Technology Architecture (TOGAF ADM: Phase D)

## Technology Stack

| Layer | Technology | Version | Justification |
|---|---|---|---|
| **Language (backend)** | Python 3.9+ | 3.9+ | Best ecosystem for AI integration, Gmail API, clear syntax |
| **Framework (backend)** | FastAPI | latest | Async, auto-generated API docs, type safety, lightweight |
| **Language (frontend)** | TypeScript | 5.x | Type safety, better developer experience than JavaScript |
| **Framework (frontend)** | Next.js (React) | 14+ | SSR, PWA support, great mobile experience, Vercel deployment |
| **Database** | PostgreSQL | 15+ | Relational data, ACID compliance, via Supabase |
| **ORM** | SQLAlchemy | 2.x | Mature, well-documented, async support |
| **Migration** | Alembic | latest | Database schema versioning, works with SQLAlchemy |
| **Testing (backend)** | pytest | latest | Standard Python testing, good async support |
| **Testing (frontend)** | Vitest | latest | Fast, Vite-native, compatible with React Testing Library |
| **Containerization** | Docker | latest | Consistent environments, easy deployment |
| **CI/CD** | GitHub Actions | N/A | Free for public repos, integrated with GitHub |
| **Hosting (frontend)** | Vercel | N/A | Free tier, optimized for Next.js, automatic deployments |
| **Hosting (backend)** | Railway | N/A | Free tier, simple Python deployments, env var management |

## Infrastructure

### Environments

| Environment | Purpose | URL/Location |
|---|---|---|
| Local | Development | `localhost:3000` (frontend), `localhost:8000` (backend) |
| Production | Live | Vercel (frontend) + Railway (backend) + Supabase (DB) |

### Deployment

- **Frontend:** Push to `main` → Vercel auto-deploys
- **Backend:** Push to `main` → Railway auto-deploys
- **Database:** Managed by Supabase (no manual deployment)
- **Local development:** Docker Compose for backend + DB, Next.js dev server for frontend

## Security Architecture

- **Authentication:** OAuth 2.0 for Gmail access (Google Cloud Console credentials). Simple token-based auth for the app itself (single user, no complex auth needed).
- **Authorization:** N/A (single user)
- **Secrets management:** `.env` locally, platform env vars in production (Railway, Vercel)
- **HTTPS:** Enforced in all environments (Vercel and Railway provide it by default)
- **Data privacy:** No bank account numbers, passwords, or sensitive credentials stored. Only transaction concepts, amounts, and account/card names.
