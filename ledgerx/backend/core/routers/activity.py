from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models import ActivityLog, User, Company, OrgUser
from auth.dependencies import get_current_user
from schemas.activity import ActivityLogList

router = APIRouter(tags=["activity"])

@router.get("/activity", response_model=ActivityLogList)
async def list_activity(
    company_id: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch activity logs for the current user/org, optionally filtered by company.
    Supports organization-wide logs even if no company is selected.
    """
    
    # Base filter: logs must belong to the user's organization context.
    # For now, we show all logs where user_id matches OR they belong to the user's org.
    
    # 1. Start with the user's own logs (universal)
    where_clause = or_(ActivityLog.user_id == current_user.id)
    
    if company_id:
        # If a company is specified, verify access to it
        company_res = await db.execute(select(Company).where(Company.id == company_id))
        company = company_res.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
            
        # Verify user belongs to same org or is an employee/admin of that org
        if (company.org_id != current_user.org_id):
            # Fallback: check OrgUser mapping
            result2 = await db.execute(
                select(OrgUser).where(OrgUser.org_id == company.org_id, OrgUser.user_id == current_user.id)
            )
            if not result2.scalar_one_or_none():
                 raise HTTPException(status_code=403, detail="Access denied to this company")
        
        # User has access, so we show logs for this specific company
        where_clause = or_(ActivityLog.company_id == company_id, ActivityLog.user_id == current_user.id)
    else:
        # If NO company is specified, we show all logs from the whole org where company_id is NULL
        # OR any log that belongs to this specific user.
        where_clause = or_(ActivityLog.user_id == current_user.id, ActivityLog.company_id == None)

    # Count total for pagination
    count_stmt = select(func.count(ActivityLog.id)).where(where_clause)
    total_res = await db.execute(count_stmt)
    total_count = total_res.scalar_one()

    # Final query with User join to get user names
    offset = (page - 1) * page_size
    stmt = (
        select(ActivityLog, User.name.label("user_name"))
        .outerjoin(User, ActivityLog.user_id == User.id)
        .where(where_clause)
        .order_by(ActivityLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    
    logs = []
    for row in result:
        log_obj, user_name = row
        # Add the labeled user_name to the object so the schema can pick it up
        log_obj.user_name = user_name
        logs.append(log_obj)

    return {
        "logs": logs,
        "total": total_count,
        "page": page,
        "page_size": page_size
    }
