# 05 — Opportunities & Solutions (TOGAF ADM: Phase E)

## Decisions Log

### Decision 1: PWA vs Native App vs Hybrid

- **Context:** App must work on FerDi's iPhone. Need to decide the frontend approach.
- **Options evaluated:**
  | Option | Pros | Cons |
  |---|---|---|
  | PWA (Next.js) | Fast to build, no App Store needed, works in Safari, easy to update | Limited iOS push notifications, no native feel |
  | Native iOS (Swift) | Best iPhone experience, full API access | Slower to build, needs App Store, harder for AI-assisted dev |
  | Hybrid (React Native / Expo) | Near-native experience, cross-platform | More complex setup, extra build step for iOS |
- **Decision:** PWA with Next.js for MVP. Migrate to React Native (Expo) when native features are needed.
- **Consequences:** MVP ships faster. UI will feel web-like but functional. Push notifications may be limited on iOS.

### Decision 2: Database Hosting

- **Context:** Need a PostgreSQL database with zero cost for MVP.
- **Options evaluated:**
  | Option | Pros | Cons |
  |---|---|---|
  | Supabase | Free tier (500MB), hosted PostgreSQL, auth built-in, REST API | Vendor dependency, free tier limits |
  | Self-hosted PostgreSQL (Docker on Railway) | Full control | Uses Railway compute, more setup |
  | SQLite (local file) | Zero config, zero cost | Not suitable for hosted backend, no concurrent access |
- **Decision:** Supabase for hosted PostgreSQL.
- **Consequences:** Free, managed database. Can use Supabase auth later if needed. Must stay within free tier limits (500MB).

### Decision 3: AI Engine for Email Analysis

- **Context:** Need an AI model to analyze emails and extract financial data.
- **Options evaluated:**
  | Option | Pros | Cons |
  |---|---|---|
  | Claude API | Excellent at structured extraction, great with Spanish content, strong reasoning | Pay per token |
  | OpenAI GPT-4 | Good extraction capabilities, widely used | Pay per token, less strong with Spanish nuance |
  | Local model (Ollama) | Free, private | Requires powerful hardware, lower quality extraction |
- **Decision:** Claude API
- **Consequences:** Small per-use cost (estimated < $5/month for personal use). Excellent extraction quality. Data sent to Anthropic API but only email content, no bank credentials.

## Build vs Buy vs Reuse

| Capability | Approach | Solution | Rationale |
|---|---|---|---|
| Email reading | Buy (API) | Gmail API | Standard, well-documented, free |
| AI analysis | Buy (API) | Claude API | Core to value proposition, best quality |
| Database | Buy (hosted) | Supabase (PostgreSQL) | Free tier, managed, no DevOps needed |
| Frontend framework | Reuse | Next.js | Open source, PWA-capable, large ecosystem |
| Backend framework | Reuse | FastAPI | Open source, Python, async, auto-docs |
| UI components | Reuse | shadcn/ui + Tailwind CSS | Open source, mobile-friendly, customizable |

## Dependencies & Risks

| Dependency / Risk | Impact | Mitigation |
|---|---|---|
| Gmail API access requires Google Cloud project setup | Blocks email ingestion | Set up OAuth consent screen early in development |
| Claude API cost could grow | Unexpected expense | Batch emails, cache results, set usage alerts |
| Supabase free tier limits (500MB) | DB full after months of use | Monitor usage, archive old data, upgrade if needed |
| Gmail email format varies by sender | AI extraction errors | Validate with FerDi daily, improve prompts over time |
| iOS PWA limitations | Limited native features | Accept for MVP, plan React Native migration for V2 |

## Work Packages

| Package | Description | Dependencies | Priority | Version |
|---|---|---|---|---|
| WP-01: Project setup | Docker, CI/CD, DB schema, project structure | None | High | V0 |
| WP-02: Gmail integration | OAuth setup, email fetching, email processing pipeline | WP-01 | High | V0 |
| WP-03: AI analysis engine | Claude API integration, prompt engineering, extraction logic | WP-01 | High | V0 |
| WP-04: Backend API | REST endpoints for movements, categories, tags | WP-01 | High | V0 |
| WP-05: Frontend PWA | Movement review UI, category/tag management, mobile-first | WP-04 | High | V0 |
| WP-06: MoneyStats export | CSV export compatible with MoneyStats import | WP-04 | Medium | V1 |
| WP-07: Advanced categorization | AI-suggested categories based on history, learning from corrections | WP-03, WP-04 | Medium | V1 |
| WP-08: React Native migration | Native iOS app with push notifications | WP-05 | Low | V2 |
