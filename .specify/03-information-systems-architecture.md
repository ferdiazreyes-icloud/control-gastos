# 03 — Information Systems Architecture (TOGAF ADM: Phase C)

## Data Architecture

### Data Entities

| Entity | Description | Key Attributes |
|---|---|---|
| Movement | A financial transaction detected from email | type, amount, currency, account, datetime, recurrence, category_id, concept, merchant, status, source_email_id |
| Category | User-defined expense category | name, icon, color, parent_category_id (for subcategories) |
| Tag | User-defined label for movements | name, color |
| MovementTag | Many-to-many relationship between movements and tags | movement_id, tag_id |
| ProcessedEmail | Record of emails already analyzed | gmail_message_id, processed_at, had_movement |

### Data Relationships

- A **Movement** belongs to one **Category** (optional, can be uncategorized)
- A **Movement** can have many **Tags** (via MovementTag)
- A **Category** can have a parent **Category** (one level of nesting)
- A **ProcessedEmail** may or may not have generated a **Movement**

### Data Storage

- **Primary database:** PostgreSQL via Supabase (transactional data, categories, tags)
- **Cache:** N/A for MVP
- **File storage:** N/A (no files stored, emails stay in Gmail)

## Application Architecture

### Components

| Component | Responsibility | Communicates With |
|---|---|---|
| Backend API | Business logic, Gmail integration, AI processing, data access | Frontend, Gmail API, Claude API, Database |
| Frontend PWA | User interface for reviewing movements, managing categories/tags | Backend API |
| Email Processor | Fetches emails from Gmail, sends to AI for analysis, saves results | Gmail API, Claude API, Database |

### External Integrations

| System | Purpose | Protocol | Notes |
|---|---|---|---|
| Gmail API | Read emails from FerDi's inbox | REST API (OAuth 2.0) | Read-only access. Scopes: gmail.readonly |
| Claude API | Analyze email content to detect and extract financial movements | REST API (API key) | Used per email batch, cost scales with volume |
| Supabase | Hosted PostgreSQL database | PostgreSQL protocol | Free tier: 500MB storage, 2 projects |
