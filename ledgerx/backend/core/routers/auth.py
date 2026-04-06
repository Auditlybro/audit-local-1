"""Auth: register, login, refresh, me."""
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import random
import os
import smtplib
from email.message import EmailMessage

from auth.dependencies import get_current_user
from auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from config import settings
from db.database import get_db
from db.redis import get_redis
from models import User, Organization, OrgUser
from schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
    GoogleLoginRequest,
    AppleLoginRequest,
    MicrosoftLoginRequest,
)
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["auth"])

class OTPSendBody(BaseModel):
    email: EmailStr

class OTPVerifyBody(BaseModel):
    email: EmailStr
    code: str

@router.post("/register", response_model=TokenResponse)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    org = Organization(
        id=uuid4(),
        name=body.org_name or "Default Org",
    )
    db.add(org)
    await db.flush()
    user = User(
        id=uuid4(),
        email=body.email,
        name=body.name,
        role="admin",
        org_id=org.id,
    )
    user.password_hash = hash_password(body.password)
    db.add(user)
    await db.flush()
    org_user = OrgUser(org_id=org.id, user_id=user.id, role="admin")
    db.add(org_user)
    await db.flush()
    access, exp = create_access_token(user.id, org.id)
    refresh = create_refresh_token(user.id)
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=exp)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not getattr(user, "password_hash", None) or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access, exp = create_access_token(user.id, user.org_id)
    refresh = create_refresh_token(user.id)
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=exp)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    access, exp = create_access_token(user.id, user.org_id)
    new_refresh = create_refresh_token(user.id)
    return TokenResponse(access_token=access, refresh_token=new_refresh, expires_in=exp)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        org_id=current_user.org_id,
    )

@router.post("/otp/send")
async def auth_otp_send(body: OTPSendBody):
    email = body.email.strip().lower()
    otp_code = str(random.randint(100000, 999999))
    r = await get_redis()
    await r.setex(f"otp:{email}", 600, otp_code)
    
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    
    if smtp_host and smtp_user and smtp_pass:
        msg = EmailMessage()
        msg.set_content(f"Your LedgerX verification code is: {otp_code}\n\nThis code expires in 10 minutes.")
        msg["Subject"] = "LedgerX Verification Code"
        msg["From"] = smtp_user
        msg["To"] = email
        try:
            target_port = smtp_port
            with smtplib.SMTP(smtp_host, target_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            print(f"OTP email sent to {email}")
        except Exception as e:
            print(f"Failed to send email: {e}")
    else:
        print(f"\n====== EMAIL MOCK ======\nTo: {email}\nCode: {otp_code}\n========================\n")
    return {"message": "OTP Sent"}


@router.post("/otp/verify", response_model=TokenResponse)
async def auth_otp_verify(body: OTPVerifyBody, db: AsyncSession = Depends(get_db)):
    email = body.email.strip().lower()
    r = await get_redis()
    stored_opt = await r.get(f"otp:{email}")
    if not stored_opt or str(stored_opt).strip() != str(body.code).strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP code")
        
    await r.delete(f"otp:{email}")
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        org = Organization(id=uuid4(), name=email.split("@")[0] + "'s Org")
        db.add(org)
        await db.flush()
        user = User(id=uuid4(), email=email, name=email.split("@")[0], role="admin", org_id=org.id)
        db.add(user)
        await db.flush()
        org_user = OrgUser(org_id=org.id, user_id=user.id, role="admin")
        db.add(org_user)
        await db.flush()
        
    access, exp = create_access_token(user.id, user.org_id)
    refresh = create_refresh_token(user.id)
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=exp)


@router.post("/google", response_model=TokenResponse)
async def auth_google(body: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    import traceback
    print(f"DEBUG: /auth/google called, credential length: {len(body.credential)}")
    try:
        from google.auth import jwt
        id_info = jwt.decode(body.credential, verify=False)
        print(f"DEBUG: Decoded Google token: email={id_info.get('email')}, name={id_info.get('name')}")
        email = id_info.get("email")
        if not email:
            raise ValueError("Google token did not provide an email address.")
        email = email.lower()
        name = id_info.get("name") or id_info.get("given_name") or email.split("@")[0]
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            org = Organization(id=uuid4(), name=name + "'s Org")
            db.add(org)
            await db.flush()
            user = User(id=uuid4(), email=email, name=name, role="admin", org_id=org.id)
            db.add(user)
            await db.flush()
            org_user = OrgUser(org_id=org.id, user_id=user.id, role="admin")
            db.add(org_user)
            await db.flush()
        
        access, exp = create_access_token(user.id, user.org_id)
        refresh = create_refresh_token(user.id)
        print(f"DEBUG: Google login SUCCESS for {email}")
        return TokenResponse(access_token=access, refresh_token=refresh, expires_in=exp)
        
    except Exception as e:
        print(f"DEBUG: Google Login Failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google Credentials")


@router.post("/apple", response_model=TokenResponse)
async def auth_apple(body: AppleLoginRequest, db: AsyncSession = Depends(get_db)):
    import traceback
    import jwt  # Using PyJWT for Apple/MS
    print(f"DEBUG: /auth/apple called")
    try:
        # In production, fetch keys from https://appleid.apple.com/auth/keys and verify
        # For this version, decoding without verification to demonstrate flow
        id_info = jwt.decode(body.credential, options={"verify_signature": False})
        print(f"DEBUG: Decoded Apple token: email={id_info.get('email')}")
        
        email = id_info.get("email")
        if not email:
             raise ValueError("Apple token did not provide an email address.")
        email = email.lower()
        name = email.split("@")[0] # Apple often lacks name in the JWT after first login
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            org = Organization(id=uuid4(), name=name + "'s Org")
            db.add(org)
            await db.flush()
            user = User(id=uuid4(), email=email, name=name, role="admin", org_id=org.id)
            db.add(user)
            await db.flush()
            org_user = OrgUser(org_id=org.id, user_id=user.id, role="admin")
            db.add(org_user)
            await db.flush()

        access, exp = create_access_token(user.id, user.org_id)
        refresh = create_refresh_token(user.id)
        return TokenResponse(access_token=access, refresh_token=refresh, expires_in=exp)
    except Exception as e:
        print(f"DEBUG: Apple Login Failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Apple Credentials")


@router.post("/microsoft", response_model=TokenResponse)
async def auth_microsoft(body: MicrosoftLoginRequest, db: AsyncSession = Depends(get_db)):
    import traceback
    import jwt
    print(f"DEBUG: /auth/microsoft called")
    try:
        # In production, fetch keys from https://login.microsoftonline.com/common/discovery/v2.0/keys
        id_info = jwt.decode(body.credential, options={"verify_signature": False})
        print(f"DEBUG: Decoded MS token: email={id_info.get('email') or id_info.get('preferred_username')}")
        
        email = id_info.get("email") or id_info.get("preferred_username")
        if not email:
            raise ValueError("Microsoft token did not provide an email address.")
        email = email.lower()
        name = id_info.get("name") or email.split("@")[0]
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            org = Organization(id=uuid4(), name=name + "'s Org")
            db.add(org)
            await db.flush()
            user = User(id=uuid4(), email=email, name=name, role="admin", org_id=org.id)
            db.add(user)
            await db.flush()
            org_user = OrgUser(org_id=org.id, user_id=user.id, role="admin")
            db.add(org_user)
            await db.flush()

        access, exp = create_access_token(user.id, user.org_id)
        refresh = create_refresh_token(user.id)
        return TokenResponse(access_token=access, refresh_token=refresh, expires_in=exp)
    except Exception as e:
        print(f"DEBUG: Microsoft Login Failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Microsoft Credentials")


