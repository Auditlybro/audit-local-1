# LedgerX

**Accounting for Indian CAs & SMEs.** Full-stack: Tally import, GST, notices, multi-user. Web, desktop (Tauri), and mobile (Expo) clients.

---

## What is LedgerX

- **Import**: Tally XML, Marg CSV, Excel, bank statements (SBI, HDFC, ICICI, Axis, Kotak)
- **Export**: Valid Tally XML for TallyPrime
- **AI**: Ghost Analyst (mismatches, duplicates, GST issues), Notice Doctor (draft replies), Tax Optimiser
- **Background jobs**: Celery (import, GSTR-1, ghost analyst, WhatsApp, GST reminders)
- **Clients**: Next.js web app, Tauri desktop (file dialogs, Ollama, single instance), Expo mobile (dashboard, new sale, reports, notifications)

---

## Setup (5 steps to run locally)

1. **Clone and install**
   ```bash
   cd ledgerx/apps/web && npm install
   cd ../desktop && npm install
   cd ../../backend && pip install -r requirements.txt
   ```

2. **Environment**
   - Copy `ledgerx/apps/web/.env.example` → `ledgerx/apps/web/.env.local`
   - Copy `ledgerx/backend/.env.example` → `ledgerx/backend/.env`
   - Set `NEXT_PUBLIC_API_URL=http://localhost:8000` (web) and `DATABASE_URL`, `REDIS_URL` (backend)

3. **Database**
   - Start Postgres and Redis (or use Docker: `docker-compose up postgres redis -d`)
   - Run migrations: `npm run db:migrate` (or your Alembic/SQL flow)
   - Optional seed: `npm run db:seed`

4. **Start backend and web**
   ```bash
   npm run dev:backend   # Terminal 1 — http://localhost:8000
   npm run dev:web       # Terminal 2 — http://localhost:3000
   ```

5. **Desktop (optional)**
   ```bash
   npm run dev:desktop   # Tauri window; ensure web is running on 3000 for embedded UI
   ```

---

## Architecture (text)

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Web       │  │  Desktop    │  │   Mobile    │
│  (Next.js)  │  │  (Tauri)    │  │  (Expo)     │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                       │
              ┌────────▼────────┐
              │  Backend (FastAPI) │  ← Health: GET /health
              │  + Celery worker   │  ← Task status: GET /tasks/:id/status
              └────────┬────────┘
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
  Postgres          Redis          (Ollama / Cloud AI)
```

---

## Import from Tally

1. In TallyPrime: Export data as **Tally XML** (Masters and/or Vouchers).
2. In LedgerX web: **Import** → choose **Tally XML** → upload the file.
3. Backend parses masters (`LEDGER` with `PARENT`, `OPENINGBALANCE`, `GSTN`) and vouchers (`VOUCHER` with `ALLLEDGERENTRIES.LIST`, `ALLINVENTORYENTRIES.LIST`), detects duplicates by GUID, and validates ledger names (exact or fuzzy match).
4. Review imported vouchers and ledgers in the app.

---

## API docs

- With backend running: **http://localhost:8000/docs** (Swagger UI).

---

## Scripts (root `package.json`)

| Script         | Description                    |
|----------------|--------------------------------|
| `dev:web`      | Start Next.js on port 3000     |
| `dev:backend`  | Start FastAPI on port 8000     |
| `dev:desktop`  | Start Tauri desktop app        |
| `dev:mobile`   | Start Expo                     |
| `dev:all`      | Run web + backend + desktop    |
| `db:migrate`   | Run migrations                 |
| `db:seed`      | Seed sample data               |
| `test:all`     | Run all tests                  |

---

## Docker

**Requires Docker Desktop (or Docker daemon) to be running.**

One-command startup:

```bash
docker-compose up
```

- **Postgres** — port 5432  
- **Redis** — port 6379  
- **Backend** — http://localhost:8000 (health: `GET /health`)  
- **Worker** — Celery consuming from Redis  
- **Web** — http://localhost:3000  

Then: create a company, upload a Tally XML file, view imported vouchers.
