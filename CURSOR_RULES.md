# Audit-Local — Cursor Rules

**Domain:** Desktop app for Indian Chartered Accountants. 100% offline. No cloud. Full DPDP compliance.

## Stack
- Frontend: Tauri (Rust) + React + TypeScript
- Backend: Python FastAPI
- AI: Ollama + Llama-3-8B (local)
- DB: ChromaDB (local vector DB)
- File parsing: Rust / Python

## Domain Context
- **Tally XML** = Indian accounting ERP export format. Contains ledgers, vouchers, transactions.
- **GST** = India's Goods and Services Tax. CAs file returns, handle notices, reconcile mismatches.
- **Mismatch** = when Tally ledger entries don't match bank statement transactions.
- All client financial data stays on the CA's laptop. **Never leaves the machine.**

## Rules (follow always)
1. **Never guess domain logic** — If Tally XML structure or GST rules are unclear, ask the user.
2. **No cloud, no leakage** — Never add cloud calls, external APIs, or telemetry of any kind.
3. **Local-only I/O** — All file I/O stays local. No uploads, no sync to external services.
4. **Boilerplate only** — Cursor writes boilerplate. User writes: GST prompt logic, scoring rules, firm-specific memory.
5. **Feature branches** — Every feature gets its own branch: `git checkout -b feature/<name>`.
