"""
LedgerX API — FastAPI. Auth stub: demo@ledgerx.in / demo123
"""
import uuid
from fastapi import FastAPI, Header, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="LedgerX API", version="0.1.0")

# --- Inline auth stub: use a router and include it first (no prefix) ---
_stub_users = {
    "demo@ledgerx.in": {
        "id": "demo-user-id",
        "email": "demo@ledgerx.in",
        "name": "Demo User",
        "role": "user",
        "org_id": "demo-org-id",
    },
}
_stub_tokens = {}

class LoginBody(BaseModel):
    email: str
    password: str

class RegisterBody(BaseModel):
    email: str
    name: str | None = None
    password: str
    org_name: str | None = None

_DEMO_RESPONSE = {"email": "demo@ledgerx.in", "password": "demo123", "hint": "Use these to sign in."}

auth_router = APIRouter(tags=["auth"])

@auth_router.get("/health")
def health():
    # If you see "build": "with-auth-demo", this main.py is running and /auth/demo exists
    return {"status": "ok", "app": "ledgerx", "build": "with-auth-demo"}

@auth_router.get("/routes")
def list_routes():
    """Debug: list registered paths (GET only)."""
    paths = []
    for r in app.routes:
        p = getattr(r, "path", None)
        if p and getattr(r, "methods", None) and "GET" in r.methods:
            paths.append(p)
    return {"paths": sorted(paths)}

@auth_router.get("/auth/demo")
def auth_demo():
    return _DEMO_RESPONSE

@auth_router.get("/demo")
def demo_alias():
    return _DEMO_RESPONSE

@auth_router.post("/auth/register")
def auth_register(body: RegisterBody):
    uid = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    _stub_users[body.email.lower()] = {
        "id": uid, "email": body.email, "name": body.name or body.email.split("@")[0],
        "role": "user", "org_id": org_id,
    }
    access, refresh = str(uuid.uuid4()), str(uuid.uuid4())
    _stub_tokens[access], _stub_tokens[refresh] = uid, uid
    return {"access_token": access, "refresh_token": refresh, "expires_in": 3600}

@auth_router.post("/auth/login")
def auth_login(body: LoginBody):
    key = (body.email or "").strip().lower()
    if key == "demo@ledgerx.in" and key not in _stub_users:
        _stub_users[key] = {"id": "demo-user-id", "email": "demo@ledgerx.in", "name": "Demo User", "role": "user", "org_id": "demo-org-id"}
    u = _stub_users.get(key)
    if not u:
        raise HTTPException(401, "Invalid email or password. Use demo@ledgerx.in / demo123")
    if key == "demo@ledgerx.in" and (body.password or "") != "demo123":
        raise HTTPException(401, "Invalid password. Use demo123")
    access, refresh = str(uuid.uuid4()), str(uuid.uuid4())
    _stub_tokens[access], _stub_tokens[refresh] = u["id"], u["id"]
    return {"access_token": access, "refresh_token": refresh, "expires_in": 3600}

@auth_router.get("/auth/me")
def auth_me(authorization: str | None = Header(None, alias="Authorization")):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    uid = _stub_tokens.get(authorization.split(" ", 1)[1])
    if not uid:
        raise HTTPException(401, "Invalid token")
    for u in _stub_users.values():
        if u["id"] == uid:
            return u
    raise HTTPException(401, "User not found")

# --- Inline companies stub ---
_stub_companies = {
    "demo-company-id": {
        "id": "demo-company-id", "org_id": "demo-org-id", "name": "Demo Company",
        "gstin": None, "pan": None, "cin": None, "address": None,
        "state_code": None, "financial_year": "2024-25", "logo_url": None,
    },
}

@auth_router.get("/companies")
def companies_list(authorization: str | None = Header(None, alias="Authorization")):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    return list(_stub_companies.values())

@auth_router.post("/companies")
def companies_create(body: dict, authorization: str | None = Header(None, alias="Authorization")):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    cid = str(uuid.uuid4())
    company = {"id": cid, "org_id": body.get("org_id") or str(uuid.uuid4()), "name": body.get("name") or "Default Company",
        "gstin": body.get("gstin"), "pan": body.get("pan"), "cin": body.get("cin"), "address": body.get("address"),
        "state_code": body.get("state_code"), "financial_year": body.get("financial_year"), "logo_url": body.get("logo_url")}
    _stub_companies[cid] = company
    return company

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional: mount task_status if core is available
try:
    import sys
    from pathlib import Path
    _B = Path(__file__).resolve().parent
    if str(_B) not in sys.path:
        sys.path.insert(0, str(_B))
    from core.routers.task_status import router as task_router
    app.include_router(task_router)
except Exception:
    pass
