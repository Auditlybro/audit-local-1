# Audit-Local

Desktop app for Indian Chartered Accountants. **100% offline.** No cloud. No data leakage. Full DPDP compliance.

## Stack
- **Frontend:** Tauri (Rust) + React + TypeScript
- **Backend:** Python FastAPI
- **AI:** Ollama + Llama-3-8B (local)
- **DB:** ChromaDB (local vector DB)
- **File parsing:** Rust / Python

## Monorepo structure
```
audit-local/
├── frontend/        # Tauri + React + TypeScript
├── backend/         # Python FastAPI
├── ai/              # Ollama integration + RAG scripts + training data
├── CURSOR_RULES.md  # Domain rules for AI assistance
└── README.md
```

## Setup
- **Backend:** `pip install -r requirements.txt` (in `backend/`)
- **Frontend:** `npm install` (in `frontend/`)
- **AI:** See `ai/` and `ai/training_data/` for RAG and training data.

## Run (exact commands)

1. **Start the FastAPI backend**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the Tauri frontend**
   ```bash
   cd frontend
   npm run tauri dev
   ```
   (Or for web-only: `npm run dev` — then open http://localhost:5173 and ensure backend is on port 8000.)

3. **Test the `/health` route**
   ```bash
   curl http://localhost:8000/health
   ```
   Expected: `{"status":"ok","app":"audit-local"}`

## Data policy
All client financial data stays on the CA's laptop. Nothing is sent to the cloud.
