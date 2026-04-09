"""Imports: Tally XML, Marg CSV, Busy XML, Excel, bank statement, GST JSON."""
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, get_company_for_user
from db.database import get_db
from models import User, Company, ImportSession
from services.import_engine import (
    parse_tally_xml_content,
    parse_marg_csv,
    parse_excel,
    validate_import,
    detect_duplicates,
    commit_import,
)
from schemas.import_export import ImportSessionResponse, ImportHistoryResponse, RollbackResponse
from utils.activity import log_activity

router = APIRouter(tags=["imports"])


async def _create_session(
    company_id: UUID,
    source_type: str,
    file_name: str | None,
    db: AsyncSession,
) -> ImportSession:
    sess = ImportSession(company_id=company_id, source_type=source_type, file_name=file_name, status="pending")
    db.add(sess)
    await db.flush()
    return sess


@router.post("/{company_id}/import/tally-xml")
async def import_tally_xml(
    file: UploadFile = File(...),
    company: Company = Depends(get_company_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    vouchers = parse_tally_xml_content(content)
    sess = await _create_session(company.id, "tally_xml", file.filename, db)
    valid, errors = await validate_import(db, company.id, vouchers)
    sess.total_records = len(vouchers)
    sess.imported_records = len(valid)
    sess.error_records = len(errors)
    sess.errors_json = [{"index": e["index"], "errors": e["errors"]} for e in errors]
    sess.status = "completed" if not errors else "partial"
    
    await log_activity(
        db, company.id, user.id, "IMPORT",
        f"Imported Tally XML: {file.filename} ({len(valid)} records)",
        {"source": "tally_xml", "filename": file.filename, "session_id": str(sess.id)}
    )
    
    await db.flush()
    return ImportSessionResponse.model_validate(sess)


@router.post("/{company_id}/import/marg-csv")
async def import_marg_csv(
    file: UploadFile = File(...),
    company: Company = Depends(get_company_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    vouchers = parse_marg_csv(content)
    sess = await _create_session(company.id, "marg_csv", file.filename, db)
    sess.total_records = len(vouchers)
    sess.status = "pending"
    
    await log_activity(
        db, company.id, user.id, "IMPORT",
        f"Started Marg CSV import: {file.filename}",
        {"source": "marg_csv", "filename": file.filename, "session_id": str(sess.id)}
    )
    
    await db.flush()
    return ImportSessionResponse.model_validate(sess)


@router.post("/{company_id}/import/busy-xml")
async def import_busy_xml(
    file: UploadFile = File(...),
    company: Company = Depends(get_company_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sess = await _create_session(company.id, "busy_xml", file.filename, db)
    
    await log_activity(
        db, company.id, user.id, "IMPORT",
        f"Started Busy XML import: {file.filename}",
        {"source": "busy_xml", "filename": file.filename, "session_id": str(sess.id)}
    )
    
    await db.flush()
    return ImportSessionResponse.model_validate(sess)


@router.post("/{company_id}/import/excel")
async def import_excel(
    file: UploadFile = File(...),
    company: Company = Depends(get_company_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    vouchers = parse_excel(content)
    sess = await _create_session(company.id, "excel", file.filename, db)
    sess.total_records = len(vouchers)
    sess.status = "pending"
    
    await log_activity(
        db, company.id, user.id, "IMPORT",
        f"Started Excel import: {file.filename}",
        {"source": "excel", "filename": file.filename, "session_id": str(sess.id)}
    )
    
    await db.flush()
    return ImportSessionResponse.model_validate(sess)


@router.post("/{company_id}/import/bank-statement")
async def import_bank_statement(
    file: UploadFile = File(...),
    company: Company = Depends(get_company_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sess = await _create_session(company.id, "bank_statement", file.filename, db)
    
    await log_activity(
        db, company.id, user.id, "IMPORT",
        f"Started Bank Statement import: {file.filename}",
        {"source": "bank_statement", "filename": file.filename, "session_id": str(sess.id)}
    )
    
    await db.flush()
    return ImportSessionResponse.model_validate(sess)


@router.post("/{company_id}/import/gst-json")
async def import_gst_json(
    file: UploadFile = File(...),
    company: Company = Depends(get_company_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sess = await _create_session(company.id, "gst_json", file.filename, db)
    
    await log_activity(
        db, company.id, user.id, "IMPORT",
        f"Started GST JSON import: {file.filename}",
        {"source": "gst_json", "filename": file.filename, "session_id": str(sess.id)}
    )
    
    await db.flush()
    return ImportSessionResponse.model_validate(sess)


@router.get("/{company_id}/import/history", response_model=ImportHistoryResponse)
async def import_history(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ImportSession).where(ImportSession.company_id == company.id).order_by(ImportSession.created_at.desc()).limit(50)
    )
    sessions = [ImportSessionResponse.model_validate(s) for s in result.scalars().all()]
    return ImportHistoryResponse(sessions=sessions)


@router.get("/{company_id}/import/sessions/{session_id}", response_model=ImportSessionResponse)
async def get_import_session(
    session_id: UUID,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ImportSession).where(ImportSession.id == session_id, ImportSession.company_id == company.id)
    )
    sess = result.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return ImportSessionResponse.model_validate(sess)


@router.post("/{company_id}/import/sessions/{session_id}/rollback", response_model=RollbackResponse)
async def rollback_import(
    session_id: UUID,
    company: Company = Depends(get_company_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ImportSession).where(ImportSession.id == session_id, ImportSession.company_id == company.id)
    )
    sess = result.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    sess.status = "rolled_back"
    
    await log_activity(
        db, company.id, user.id, "IMPORT_ROLLBACK",
        f"Rolled back import session item: {sess.file_name or sess.id}",
        {"session_id": str(session_id), "source": sess.source_type}
    )
    
    await db.flush()
    return RollbackResponse(session_id=session_id, rolled_back=True, message="Session marked as rolled back")
