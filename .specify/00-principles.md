# 00 — Principles (TOGAF ADM: Preliminary)

> Immutable principles for this project. DO NOT modify unless FerDi explicitly requests it.

## Purpose

Define the non-negotiable rules and constraints that guide ALL decisions in this project.

## Principles

| # | Principle | Rationale |
|---|---|---|
| 1 | Privacy by default | Only concepts, amounts, and account names are stored. Never bank account numbers, passwords, or sensitive financial credentials. |
| 2 | Mobile-first | The app must work well on iPhone (Safari). Every UI decision starts from the mobile experience. |
| 3 | MVP first | Build the minimum useful thing, validate, then iterate. No premature optimization or over-engineering. |
| 4 | Single user | Designed for FerDi only. No multi-tenant architecture, no user management complexity. |
| 5 | AI assists, human decides | AI suggests movements from emails. FerDi always confirms, corrects, or discards. No automatic financial actions. |

## Constraints

- Budget: $0 for infrastructure in MVP phase (free tiers only)
- Single developer (AI-assisted)
- Must work on iPhone via Safari (PWA)
- Gmail is the primary data source for expense detection
- Claude API is the AI engine for email analysis
