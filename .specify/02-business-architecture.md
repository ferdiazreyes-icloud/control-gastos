# 02 — Business Architecture (TOGAF ADM: Phase B)

## User Flows

### Flow A: Automatic Email Ingestion & Analysis

1. System connects to FerDi's Gmail account (via Gmail API)
2. System fetches new/unprocessed emails since last check
3. AI (Claude API) analyzes each email to determine if it contains a financial movement
4. For emails with movements: AI extracts type, amount, currency, account/card, date/time, merchant/concept, and suggests a category
5. Extracted movements are saved with status "pending" in the database
6. System marks processed emails to avoid reprocessing

### Flow B: Daily Review on iPhone

1. FerDi opens the app on his iPhone (PWA via Safari)
2. App shows today's pending movements (list view)
3. For each movement, FerDi can:
   - **Confirm** — movement is correct as detected
   - **Edit** — correct any field (amount, category, account, etc.)
   - **Discard** — not a real movement (false positive)
4. Confirmed movements are saved as final records
5. FerDi can also browse past days to review/edit

## Use Cases

| # | Use Case | Actor | Description |
|---|---|---|---|
| UC-01 | Ingest emails | System | Fetch and analyze new emails from Gmail |
| UC-02 | Review daily movements | FerDi | View, confirm, edit, or discard detected movements |
| UC-03 | Manage categories | FerDi | Create, edit, delete custom expense categories |
| UC-04 | Manage tags | FerDi | Create, edit, delete custom tags for movements |
| UC-05 | Browse history | FerDi | View confirmed movements from past days |

## Business Rules

- A movement starts as "pending" until FerDi confirms or discards it
- The AI suggests a category but FerDi always has final say
- No financial data beyond concept, amount, and account name is stored
- Emails are only read, never modified or deleted
- Each email is processed only once (idempotent ingestion)

## Business Processes

1. **Daily ingestion** — System checks Gmail periodically (or on demand) for new emails with financial movements
2. **Daily review** — FerDi reviews pending movements, typically once a day
3. **Category management** — FerDi maintains his own category and tag taxonomy over time
