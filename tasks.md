# Tasks — Control Gastos

> Version roadmap and task tracking. Updated as work progresses.

---

## V0 — MVP: Gmail → AI → Daily Review List

Goal: FerDi can open the app on his iPhone, see expenses detected from his Gmail, and confirm/discard them.

### Phase 1: Project Foundation
- [ ] Backend project structure (FastAPI, Docker, Makefile)
- [ ] Database schema design and initial migration (Supabase/PostgreSQL)
- [ ] Frontend project structure (Next.js, PWA config, Tailwind + shadcn/ui)
- [ ] Docker Compose for local development
- [ ] CI/CD pipeline (GitHub Actions: lint, test, build)

### Phase 2: Gmail Integration
- [ ] Google Cloud project setup (OAuth consent screen, credentials)
- [ ] Gmail OAuth 2.0 flow (authenticate FerDi's account)
- [ ] Email fetching service (read new emails since last check)
- [ ] Email deduplication (track processed emails, avoid reprocessing)

### Phase 3: AI Analysis Engine
- [ ] Claude API integration (client, error handling, retry logic)
- [ ] Prompt engineering for financial movement detection in emails
- [ ] Structured extraction: type, amount, currency, account, date, concept/merchant
- [ ] Category suggestion based on merchant/concept
- [ ] Email processing pipeline (fetch → analyze → store)

### Phase 4: Backend API
- [ ] CRUD endpoints for movements (list, update status, edit)
- [ ] CRUD endpoints for categories
- [ ] CRUD endpoints for tags
- [ ] Filter movements by date, status, category
- [ ] Trigger email ingestion endpoint (on-demand processing)

### Phase 5: Frontend PWA
- [ ] PWA setup (manifest, service worker, installable on iPhone)
- [ ] Daily movement review screen (list of pending movements)
- [ ] Confirm/edit/discard flow for each movement
- [ ] Category management screen
- [ ] Tag management screen
- [ ] History view (browse confirmed movements by date)
- [ ] Mobile-first responsive design

### Phase 6: Integration & Polish
- [ ] End-to-end flow testing (Gmail → AI → API → UI)
- [ ] Error handling and edge cases
- [ ] Performance optimization (< 3s load time on iPhone)
- [ ] User acceptance testing with FerDi

---

## V1 — Enhanced Intelligence & MoneyStats Bridge

Goal: Smarter categorization and ability to export data to MoneyStats.

- [ ] CSV export compatible with MoneyStats import format
- [ ] AI-suggested categories based on historical confirmation patterns
- [ ] Recurring movement detection (subscriptions, monthly bills)
- [ ] Batch confirm/discard for similar movements
- [ ] Basic spending summary (daily, weekly, monthly totals)

---

## V2 — Full Replacement

Goal: Replace MoneyStats entirely with a native, AI-powered experience.

- [ ] React Native (Expo) migration for native iOS app
- [ ] Push notifications for new detected movements
- [ ] Manual expense entry (for cash/non-email expenses)
- [ ] Budget tracking and alerts
- [ ] Advanced reporting and analytics
- [ ] Multi-source ingestion (SMS, WhatsApp, bank app notifications)
