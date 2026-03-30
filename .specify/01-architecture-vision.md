# 01 — Architecture Vision (TOGAF ADM: Phase A)

## Problem Statement

FerDi tracks personal expenses manually using MoneyStats. One of his main data sources is Gmail, where he receives transaction notifications, receipts, and purchase confirmations. Today, he must read each email, identify which ones are financial movements, and manually enter them into MoneyStats. This is tedious, time-consuming, and prone to missing transactions.

## Stakeholders

| Stakeholder | Role | Concern |
|---|---|---|
| FerDi | Solo user and project owner | Simple, fast daily review of expenses detected from email. Must work on iPhone. |

## Solution Overview

A service that connects to FerDi's Gmail account, reads incoming emails, uses AI (Claude API) to detect financial movements (charges, receipts, transfers, deposits), extracts the relevant data (amount, merchant, date, account/card), and presents a daily list that FerDi can review, confirm, or discard from his iPhone.

## Scope

**In scope (MVP):**
- Connect to Gmail API and read emails
- AI-powered detection of financial movements in emails
- Extract: type (income/expense/transfer), amount, currency, account/card, date/time, merchant/concept
- Daily list of detected movements viewable on iPhone
- Confirm/correct/discard each movement
- Custom categories and tags (managed by FerDi)

**Out of scope (future):**
- Integration with MoneyStats (export/import via CSV or automated)
- Recurring movement detection
- Advanced reporting and analytics
- Budget tracking and alerts
- Multi-source ingestion (SMS, WhatsApp, bank apps)
- Full MoneyStats replacement

## Value Proposition

Save FerDi 15-30 minutes of daily manual work reviewing emails and entering expenses. Reduce missed transactions. Build the foundation for eventually replacing MoneyStats with a smarter, AI-powered expense tracker.
