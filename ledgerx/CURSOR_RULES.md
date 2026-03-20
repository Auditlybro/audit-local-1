# LedgerX — Cursor Rules

**Product:** Full-stack accounting platform for Indian CAs and SME business owners. Competes with TallyPrime, Marg ERP, Busy Accounting.

## Stack
- **Frontend:** Next.js 14 + TypeScript + TailwindCSS
- **Desktop:** Tauri + React (apps/desktop)
- **Backend:** Python FastAPI (microservices: core, ai, worker)
- **Database:** PostgreSQL + Redis
- **Vector DB:** ChromaDB (AI features)
- **Auth:** Supabase Auth (multi-tenant)
- **Storage:** Local + S3-compatible
- **Queue:** Celery + Redis

## Domain Knowledge

### Tally XML
- Format uses `TALLYMESSAGE` > `VOUCHER` tags.
- 28 predefined ledger groups: 15 primary, 13 sub-groups (Tally-compatible).
- 24 voucher types: Payment, Receipt, Journal, Contra, Sales, Purchase, Credit Note, Debit Note, plus inventory voucher types.

### Indian GST
- **CGST + SGST** for intrastate supply.
- **IGST** for interstate supply.
- GSTIN format: 2 digits state + 10 char PAN + 1 entity + 1 Z + 1 check digit.

### Indian Conventions
- **Number format:** 1,00,000 (lakhs) not 100,000.
- **Financial year:** April 1 to March 31.
- **Currency:** All amounts in Indian Rupees (₹).

## Monorepo
- `apps/web` — Next.js 14 web app
- `apps/desktop` — Tauri + React desktop
- `apps/mobile` — React Native (scaffold)
- `backend/core` — FastAPI main app
- `backend/ai` — AI/LLM services
- `backend/worker` — Celery jobs
- `packages/ui` — Shared React components
- `packages/types` — Shared TypeScript types
- `packages/utils` — Shared utilities
- `database/migrations` — SQL migrations
- `database/seeds` — Seed data

## Rules
- Follow multi-tenant patterns: all company-scoped data filtered by `company_id` / `org_id`.
- Use Indian number and date formatting in UI and exports.
- GSTIN and PAN validation where applicable.
