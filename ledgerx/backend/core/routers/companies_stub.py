"""
Stub companies endpoints so the register wizard can create a company and list it.
Replace with real DB later.
"""
import uuid
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

router = APIRouter(tags=["companies"])

# In-memory: company_id -> company. Demo company so sign-in works without registering.
_demo_company_id = "demo-company-id"
_stub_companies: dict[str, dict] = {
    _demo_company_id: {
        "id": _demo_company_id,
        "org_id": "demo-org-id",
        "name": "Demo Company",
        "gstin": None,
        "pan": None,
        "cin": None,
        "address": None,
        "state_code": None,
        "financial_year": "2024-25",
        "logo_url": None,
    },
}


class CompanyBody(BaseModel):
    name: str | None = None
    gstin: str | None = None
    pan: str | None = None
    state_code: str | None = None
    financial_year: str | None = None
    org_id: str | None = None
    address: str | None = None
    cin: str | None = None
    logo_url: str | None = None


def _require_auth(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    return authorization.split(" ", 1)[1]


@router.get("/companies")
def list_companies(authorization: str | None = Header(None, alias="Authorization")):
    _require_auth(authorization)
    return list(_stub_companies.values())


@router.post("/companies")
def create_company(
    body: CompanyBody,
    authorization: str | None = Header(None, alias="Authorization"),
):
    _require_auth(authorization)
    cid = str(uuid.uuid4())
    company = {
        "id": cid,
        "org_id": body.org_id or str(uuid.uuid4()),
        "name": body.name or "Default Company",
        "gstin": body.gstin,
        "pan": body.pan,
        "cin": body.cin,
        "address": body.address,
        "state_code": body.state_code,
        "financial_year": body.financial_year,
        "logo_url": body.logo_url,
    }
    _stub_companies[cid] = company
    return company


@router.get("/companies/{company_id}")
def get_company(
    company_id: str,
    authorization: str | None = Header(None, alias="Authorization"),
):
    _require_auth(authorization)
    if company_id not in _stub_companies:
        raise HTTPException(status_code=404, detail="Company not found")
    return _stub_companies[company_id]


@router.put("/companies/{company_id}")
def update_company(
    company_id: str,
    body: CompanyBody,
    authorization: str | None = Header(None, alias="Authorization"),
):
    _require_auth(authorization)
    if company_id not in _stub_companies:
        raise HTTPException(status_code=404, detail="Company not found")
    c = _stub_companies[company_id]
    for k, v in body.model_dump(exclude_unset=True).items():
        if v is not None:
            c[k] = v
    return c


@router.delete("/companies/{company_id}")
def delete_company(
    company_id: str,
    authorization: str | None = Header(None, alias="Authorization"),
):
    _require_auth(authorization)
    if company_id not in _stub_companies:
        raise HTTPException(status_code=404, detail="Company not found")
    del _stub_companies[company_id]
    return {"ok": True}
