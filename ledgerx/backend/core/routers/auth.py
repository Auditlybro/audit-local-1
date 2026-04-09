"""Auth: register, login, refresh, me."""
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select, or_
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
    ProfileSetupRequest,
    GoogleLoginRequest,
    AppleLoginRequest,
    MicrosoftLoginRequest,
)
from pydantic import BaseModel, EmailStr
from utils.activity import log_activity_background

router = APIRouter(tags=["auth"])


class OTPSendBody(BaseModel):
    email: EmailStr

class OTPVerifyBody(BaseModel):
    email: EmailStr
    code: str

@router.post("/register", response_model=TokenResponse)
async def register(
    body: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    email = body.email.strip().lower()
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        method = existing_user.auth_method.title() if hasattr(existing_user, "auth_method") else "Manual"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Email already registered via {method}. Please use your original login method."
        )

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
    await db.commit()
    background_tasks.add_task(
        log_activity_background, None, user.id, "USER_REGISTER",
        f"User registered with {body.email}",
        {"org_name": body.org_name}
    )
    # log_activity requires company_id (NOT NULL); auth events have no company context, skip.
    access, exp = create_access_token(user.id, org.id)
    refresh = create_refresh_token(user.id)
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=exp)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    # Search by email OR username
    result = await db.execute(
        select(User).where((User.email == body.identifier.lower()) | (User.username == body.identifier))
    )
    user = result.scalar_one_or_none()
    
    if not user or not getattr(user, "password_hash", None) or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    background_tasks.add_task(
        log_activity_background, None, user.id, "USER_LOGIN",
        f"User logged in via Manual Credentials: {user.email}"
    )
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
    # If name, username, or password_hash is missing, profile setup is needed
    # (Except for social-only users who might skip password, but let's assume they need a name/username)
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        name=current_user.name,
        role=current_user.role,
        org_id=current_user.org_id,
        profile_setup_needed=current_user.name is None or current_user.org_id is None,
        is_social=(current_user.auth_method != "manual")
    )


@router.post("/setup-profile", response_model=UserResponse)
async def setup_profile(
    body: ProfileSetupRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Complete profile setup after initial OTP/Social login."""
    print(f"DEBUG: setup_profile started for user {user.email}")
    try:
        user.name = body.name
        user.username = body.username
        if body.password:
            user.password_hash = hash_password(body.password)
            print("DEBUG: Password hashed.")
        
        # Update organization name if provided
        if body.org_name and user.org_id:
            print(f"DEBUG: Updating org name to {body.org_name}")
            result = await db.execute(select(Organization).where(Organization.id == user.org_id))
            org = result.scalar_one_or_none()
            if org:
                org.name = body.org_name
                print("DEBUG: Org name updated.")
                
        await db.flush()
        print("DEBUG: db.flush() success.")
        await db.commit()
        print("DEBUG: db.commit() success.")
        await db.refresh(user)
        background_tasks.add_task(
            log_activity_background, None, user.id, "PROFILE_SETUP",
            f"User completed profile setup: {user.name} ({user.username})",
            {"email": user.email}
        )
        print("DEBUG: Profile setup COMPLETE.")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            name=user.name,
            role=user.role,
            org_id=user.org_id,
            profile_setup_needed=user.name is None or user.org_id is None,
            is_social=(user.auth_method != "manual")
        )
    except Exception as e:
        import traceback
        print(f"ERROR in setup_profile: {e}")
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during setup: {str(e)}")

def send_otp_email(email: str, otp_code: str):
    smtp_host = settings.smtp_host
    smtp_user = settings.smtp_user
    smtp_pass = settings.smtp_pass
    smtp_port = settings.smtp_port
    
    if smtp_host and smtp_user and smtp_pass:
        try:
            msg = EmailMessage()
            msg.set_content(f"Your LedgerX verification code is: {otp_code}\n\nThis code expires in 10 minutes.")
            msg["Subject"] = "LedgerX Verification Code"
            msg["From"] = smtp_user
            msg["To"] = email
            
            with smtplib.SMTP(smtp_host, smtp_port, timeout=5) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            print(f"OTP email sent to {email}")
        except Exception as e:
            print(f"Failed to send email: {e}")
            print(f"DEV MOCK OTP: {otp_code}")
    else:
        print(f"\n====== EMAIL MOCK ======\nTo: {email}\nCode: {otp_code}\n========================\n")

@router.post("/otp/send")
async def auth_otp_send(
    body: OTPSendBody, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    email = body.email.strip().lower()
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if user:
        # If the user is fully registered (has a name or password), they shouldn't be "registering" again.
        if user.auth_method != "manual":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"This email is registered via {user.auth_method.title()}. Please use Social Login."
            )
        
        # If they are a manual user and already have a name/password, they are fully registered.
        if user.name and user.password_hash:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="This email is already registered. Please sign in instead."
            )
    otp_code = str(random.randint(100000, 999999))
    
    try:
        r = await get_redis()
        await r.setex(f"otp:{email}", 600, otp_code)
    except Exception as re:
        print(f"Redis error: {re}")
    
    background_tasks.add_task(send_otp_email, email, otp_code)
    
    return {"message": "OTP Sent"}


@router.post("/otp/verify", response_model=TokenResponse)
async def auth_otp_verify(
    body: OTPVerifyBody, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    email = body.email.strip().lower()
    r = await get_redis()
    stored_opt = await r.get(f"otp:{email}")
    if not stored_opt or str(stored_opt).strip() != str(body.code).strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP code")
        
    await r.delete(f"otp:{email}")
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create a placeholder organization
        org = Organization(id=uuid4(), name=email.split("@")[0] + "'s Firm")
        db.add(org)
        await db.flush()
        # Create user with name=None and username=None to flag for setup
        user = User(
            id=uuid4(),
            email=email,
            name=None,
            username=None,
            role="admin",
            org_id=org.id,
            password_hash=None,
            auth_method="manual"
        )
        db.add(user)
        await db.flush()
        org_user = OrgUser(org_id=org.id, user_id=user.id, role="admin")
        db.add(org_user)
        await db.flush()
        
    await db.commit()
    background_tasks.add_task(
        log_activity_background, None, user.id, "USER_OTP_VERIFY",
        f"User verified email/OTP: {user.email}"
    )
    # log_activity requires company_id (NOT NULL); auth events have no company context, skip.
    access, exp = create_access_token(user.id, user.org_id)
    refresh = create_refresh_token(user.id)
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=exp)


@router.post("/google", response_model=TokenResponse)
async def auth_google(
    body: GoogleLoginRequest, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    import traceback
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
            user = User(
                id=uuid4(), 
                email=email, 
                name=name, 
                username=None, 
                role="admin", 
                org_id=org.id,
                password_hash=None,
                auth_method="google"
            )
            db.add(user)
            await db.flush()
            org_user = OrgUser(org_id=org.id, user_id=user.id, role="admin")
            db.add(org_user)
            await db.flush()
        
        await db.commit()
        background_tasks.add_task(
            log_activity_background, None, user.id, "USER_LOGIN",
            f"User logged in via Google: {user.email}"
        )
        # log_activity requires company_id (NOT NULL); auth events have no company context, skip.
        access, exp = create_access_token(user.id, user.org_id)
        refresh = create_refresh_token(user.id)
        print(f"DEBUG: Google login SUCCESS for {email}")
        return TokenResponse(access_token=access, refresh_token=refresh, expires_in=exp)
        
    except Exception as e:
        traceback.print_exc()
        # #region agent log
        import json as _gjson, time as _gtime
        from pathlib import Path as _gPath
        _glp = _gPath(__file__).resolve().parents[4] / "debug-e34ec7.log"
        with _glp.open("a", encoding="utf-8") as _gf:
            _gf.write(_gjson.dumps({"sessionId":"e34ec7","runId":"login-debug-2","hypothesisId":"G4","location":"auth.py:google:except","message":"Google auth exception","data":{"errorType":type(e).__name__,"errorMessage":str(e)[:400]},"timestamp":int(_gtime.time()*1000)})+"\n")
        # #endregion
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google Credentials")


@router.post("/apple", response_model=TokenResponse)
async def auth_apple(
    body: AppleLoginRequest, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    import traceback
    import jwt  # Using PyJWT for Apple/MS
    print(f"DEBUG: /auth/apple called")
    try:
        id_info = jwt.decode(body.credential, options={"verify_signature": False})
        print(f"DEBUG: Decoded Apple token: email={id_info.get('email')}")
        
        email = id_info.get("email")
        if not email:
             raise ValueError("Apple token did not provide an email address.")
        email = email.lower()
        name = email.split("@")[0]
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            org = Organization(id=uuid4(), name=name + "'s Org")
            db.add(org)
            await db.flush()
            user = User(
                id=uuid4(), 
                email=email, 
                name=name, 
                username=None, 
                role="admin", 
                org_id=org.id,
                password_hash=None,
                auth_method="apple"
            )
            db.add(user)
            await db.flush()
            org_user = OrgUser(org_id=org.id, user_id=user.id, role="admin")
            db.add(org_user)
            await db.flush()
        
        await db.commit()
        background_tasks.add_task(
            log_activity_background, None, user.id, "USER_LOGIN",
            f"User logged in via Apple: {user.email}"
        )

        access, exp = create_access_token(user.id, user.org_id)
        refresh = create_refresh_token(user.id)
        return TokenResponse(access_token=access, refresh_token=refresh, expires_in=exp)
    except Exception as e:
        print(f"DEBUG: Apple Login Failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Apple Credentials")


@router.post("/microsoft", response_model=TokenResponse)
async def auth_microsoft(
    body: MicrosoftLoginRequest, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    import traceback
    import jwt
    # #region agent log
    import json as _json, time as _time
    from pathlib import Path as _Path
    def _mslog(hid, loc, msg, data):
        _lp = _Path(__file__).resolve().parents[4] / "debug-e34ec7.log"
        with _lp.open("a", encoding="utf-8") as _f:
            _f.write(_json.dumps({"sessionId":"e34ec7","runId":"ms-debug-1","hypothesisId":hid,"location":loc,"message":msg,"data":data,"timestamp":int(_time.time()*1000)})+"\n")
    _mslog("H1","auth.py:ms:entry","Microsoft auth entry",{"credentialLen":len(body.credential) if body.credential else 0})
    # #endregion
    try:
        id_info = jwt.decode(body.credential, options={"verify_signature": False})
        # #region agent log
        email_found = id_info.get("email") or id_info.get("preferred_username")
        _mslog("H2","auth.py:ms:decoded","Token decoded",{"email":email_found,"keys":list(id_info.keys())[:10]})
        # #endregion
        
        email = id_info.get("email") or id_info.get("preferred_username")
        if not email:
            raise ValueError("Microsoft token did not provide an email address.")
        email = email.lower()
        name = id_info.get("name") or email.split("@")[0]
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        # #region agent log
        _mslog("H3","auth.py:ms:user-lookup","User lookup done",{"found":user is not None,"email":email})
        # #endregion
        
        if not user:
            org = Organization(id=uuid4(), name=name + "'s Org")
            db.add(org)
            await db.flush()
            user = User(
                id=uuid4(), 
                email=email, 
                name=name, 
                username=None, 
                role="admin", 
                org_id=org.id,
                password_hash=None,
                auth_method="microsoft"
            )
            db.add(user)
            await db.flush()
            org_user = OrgUser(org_id=org.id, user_id=user.id, role="admin")
            db.add(org_user)
            await db.flush()

        await db.commit()
        background_tasks.add_task(
            log_activity_background, None, user.id, "USER_LOGIN",
            f"User logged in via Microsoft: {user.email}"
        )
        access, exp = create_access_token(user.id, user.org_id)
        refresh = create_refresh_token(user.id)
        # #region agent log
        _mslog("H4","auth.py:ms:success","Microsoft login success",{"email":email,"hasToken":bool(access)})
        # #endregion
        return TokenResponse(access_token=access, refresh_token=refresh, expires_in=exp)
    except Exception as e:
        traceback.print_exc()
        # #region agent log
        _mslog("H5","auth.py:ms:except","Microsoft auth exception",{"errorType":type(e).__name__,"errorMessage":str(e)[:300]})
        # #endregion
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Microsoft Credentials")


