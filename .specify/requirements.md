# Requirements Management (TOGAF ADM: Continuous)

> Living document. Updated throughout the project lifecycle as new requirements emerge or existing ones change.

## Functional Requirements

| ID | Requirement | Priority | Status | Version |
|---|---|---|---|---|
| FR-01 | Connect to Gmail via OAuth 2.0 and fetch emails | Must have | Done | V0 |
| FR-02 | AI analyzes each email to detect financial movements | Must have | Done | V0 |
| FR-03 | Extract from movements: type (income/expense/transfer), amount, currency, account/card, date/time, concept/merchant | Must have | Done | V0 |
| FR-04 | Store detected movements with status "pending" | Must have | Done | V0 |
| FR-05 | Display daily list of pending movements on iPhone | Must have | Pending | V0 |
| FR-06 | Confirm, edit, or discard each pending movement | Must have | Pending | V0 |
| FR-07 | Manage custom categories (CRUD) | Must have | Done | V0 |
| FR-08 | Manage custom tags (CRUD) | Must have | Done | V0 |
| FR-09 | Browse confirmed movements by date | Must have | Done | V0 |
| FR-10 | Mark processed emails to avoid reprocessing | Must have | Done | V0 |
| FR-11 | Export movements to CSV (MoneyStats compatible) | Should have | Pending | V1 |
| FR-12 | AI suggests category based on historical patterns | Could have | Pending | V1 |
| FR-13 | Detect recurring movements (subscriptions, etc.) | Could have | Pending | V1 |
| FR-14 | Push notifications for new detected movements | Could have | Pending | V2 |

## Non-Functional Requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-01 | Performance | Page load time on iPhone | < 3 seconds |
| NFR-02 | Performance | Email processing time per batch | < 30 seconds for 50 emails |
| NFR-03 | Security | No sensitive bank data stored | Only concepts, amounts, account names |
| NFR-04 | Security | Gmail access via OAuth 2.0 | Read-only scope (gmail.readonly) |
| NFR-05 | Security | HTTPS enforced | All environments |
| NFR-06 | Privacy | Email content not persisted | Only extracted movement data is stored |
| NFR-07 | Cost | Infrastructure cost | $0 (free tiers) for MVP |
| NFR-08 | Usability | Mobile-first responsive design | Optimized for iPhone screen sizes |
| NFR-09 | Reliability | Idempotent email processing | Each email processed exactly once |

## Acceptance Criteria (MVP)

- [ ] FerDi can authenticate with his Gmail account
- [ ] System fetches and analyzes emails from Gmail
- [ ] Financial movements are correctly detected and extracted from emails
- [ ] FerDi can see a daily list of pending movements on his iPhone
- [ ] FerDi can confirm, edit, or discard each movement
- [ ] FerDi can create and manage custom categories and tags
- [ ] Confirmed movements are stored and browsable by date
- [ ] FerDi can validate detected records against his actual emails and confirm they are correct

## Requirements Change Log

| Date | Change | Reason | Impact |
|---|---|---|---|
| 2026-03-29 | Initial requirements defined | Project kickoff | All ADM artifacts created |
