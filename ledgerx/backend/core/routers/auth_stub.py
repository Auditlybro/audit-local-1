"""
Stub auth endpoints so the register wizard can complete without a real DB.
Replace with Supabase or your auth backend later.
"""
import uuid
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory stub storage (replace with DB). Demo user so you can sign in without registering.
_demo_uid = "demo-user-id"
_demo_org = "demo-org-id"
_stub_users: dict[str, dict] = {
    "demo@ledgerx.in": {
        "id": _demo_uid,
        "email": "demo@ledgerx.in",
        "name": "Demo User",
        "role": "user",
        "org_id": _demo_org,
    },
}
_stub_tokens: dict[str, str] = {}  # token -> user_id


class RegisterBody(BaseModel):
    email: str
    name: str | None = None
    password: str
    org_name: str | None = None


class LoginBody(BaseModel):
    email: str
    password: str


class RefreshBody(BaseModel):
    refresh_token: str


@router.post("/register")
def register(body: RegisterBody):
    uid = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    _stub_users[body.email.lower()] = {
        "id": uid,
        "email": body.email,
        "name": body.name or body.email.split("@")[0],
        "role": "user",
        "org_id": org_id,
    }
    access = str(uuid.uuid4())
    refresh = str(uuid.uuid4())
    _stub_tokens[access] = uid
    _stub_tokens[refresh] = uid
    return {
        "access_token": access,
        "refresh_token": refresh,
        "expires_in": 3600,
    }


@router.post("/login")
def login(body: LoginBody):
    key = (body.email or "").strip().lower()
    # Ensure demo user exists (in case backend wasn't restarted after we added it)
    if key == "demo@ledgerx.in" and key not in _stub_users:
        _stub_users[key] = {
            "id": _demo_uid,
            "email": "demo@ledgerx.in",
            "name": "Demo User",
            "role": "user",
            "org_id": _demo_org,
        }
    u = _stub_users.get(key)
    if not u:
        raise HTTPException(status_code=401, detail="Invalid email or password. Register first, or use demo@ledgerx.in / demo123")
    if key == "demo@ledgerx.in" and (body.password or "") != "demo123":
        raise HTTPException(status_code=401, detail="Invalid email or password. Use password: demo123")
    access = str(uuid.uuid4())
    refresh = str(uuid.uuid4())
    _stub_tokens[access] = u["id"]
    _stub_tokens[refresh] = u["id"]
    return {
        "access_token": access,
        "refresh_token": refresh,
        "expires_in": 3600,
    }


@router.post("/refresh")
def refresh(body: RefreshBody):
    uid = _stub_tokens.get(body.refresh_token)
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access = str(uuid.uuid4())
    _stub_tokens[access] = uid
    return {"access_token": access, "refresh_token": body.refresh_token, "expires_in": 3600}


@router.get("/demo")
def demo_info():
    """Return demo credentials so you can verify stub auth is loaded."""
    return {"email": "demo@ledgerx.in", "password": "demo123", "hint": "Use these to sign in."}


@router.get("/me")
def me(authorization: str | None = Header(None, alias="Authorization")):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    uid = _stub_tokens.get(token)
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token")
    for u in _stub_users.values():
        if u["id"] == uid:
            return u
    raise HTTPException(status_code=401, detail="User not found")
