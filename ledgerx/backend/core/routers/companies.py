"""Companies CRUD."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, get_company_for_user
from db.database import get_db
from models import User, Company
from schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse

router = APIRouter(tags=["companies"])


from utils.activity import log_activity_background
from sqlalchemy import select, or_

@router.get("", response_model=list[CompanyResponse])
async def list_companies(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from models import OrgUser
    
    # log_activity requires company_id (NOT NULL); listing all companies has no single-company context, skip.

    # Subquery for all orgs the user belongs to via OrgUser
    org_user_stmt = select(OrgUser.org_id).where(OrgUser.user_id == current_user.id)
    
    # Select all companies that belong to those orgs OR the user's primary org_id
    stmt = select(Company).where(
        or_(
            Company.org_id == current_user.org_id,
            Company.org_id.in_(org_user_stmt)
        )
    )
    
    result = await db.execute(stmt)
    companies = result.scalars().all()
    return [CompanyResponse.model_validate(c) for c in companies]


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    body: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has no organization")
    company = Company(
        org_id=current_user.org_id,
        name=body.name,
        gstin=body.gstin,
        pan=body.pan,
        cin=body.cin,
        address=body.address,
        state_code=body.state_code,
        financial_year=body.financial_year,
        logo_url=body.logo_url,
    )
    db.add(company)
    await db.flush()
    return CompanyResponse.model_validate(company)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company: Company = Depends(get_company_for_user),
):
    return CompanyResponse.model_validate(company)


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    body: CompanyUpdate,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    if body.name is not None:
        company.name = body.name
    if body.gstin is not None:
        company.gstin = body.gstin
    if body.pan is not None:
        company.pan = body.pan
    if body.cin is not None:
        company.cin = body.cin
    if body.address is not None:
        company.address = body.address
    if body.state_code is not None:
        company.state_code = body.state_code
    if body.financial_year is not None:
        company.financial_year = body.financial_year
    if body.logo_url is not None:
        company.logo_url = body.logo_url
    await db.flush()
    return CompanyResponse.model_validate(company)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    await db.delete(company)
    await db.flush()
