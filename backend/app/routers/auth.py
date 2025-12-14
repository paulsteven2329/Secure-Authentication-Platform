from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.user import Token, UserCreate
from app.crud.user import authenticate_user, create_user, get_user_by_email
from app.core.security import create_access_token, create_refresh_token, revoke_token
from app.dependencies import get_db, get_current_user, login_rate_limiter
from app.models.user import User
import jwt
from app.core.config import settings
from authlib.integrations.starlette_client import OAuth
from authlib.common.errors import AuthlibHTTPError

router = APIRouter()

# OAuth setup
oauth = OAuth()

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    client_kwargs={'scope': 'openid email profile'}
)

oauth.register(
    name='github',
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    userinfo_endpoint='https://api.github.com/user',
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    client_kwargs={'scope': 'read:user user:email'}
)

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = create_user(db, user)
    access_token = create_access_token({"sub": new_user.email, "role": new_user.role})
    refresh_token = create_refresh_token({"sub": new_user.email, "role": new_user.role})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/login", response_model=Token, dependencies=[login_rate_limiter()])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token({"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.email, "role": user.role})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
def refresh_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Refresh token required")
    refresh_token_str = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(refresh_token_str, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("scope") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        email = payload["sub"]
        access_token = create_access_token({"sub": email, "role": payload.get("role")})
        return {"access_token": access_token, "token_type": "bearer"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout")
def logout(request: Request, current_user: User = Depends(get_current_user)):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                revoke_token(jti, exp)
        except:
            pass
    return {"msg": "Logged out successfully"}

# Google OAuth
@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = f"{settings.APP_URL}/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo') or (await oauth.google.parse_id_token(token))
        email = user_info["email"]
    except AuthlibHTTPError:
        raise HTTPException(status_code=400, detail="Google OAuth failed")
    db_user = get_user_by_email(db, email)
    if not db_user:
        db_user = create_user(db, UserCreate(email=email, password=str(uuid.uuid4()), role="user"))
    access_token = create_access_token({"sub": db_user.email, "role": db_user.role})
    refresh_token = create_refresh_token({"sub": db_user.email, "role": db_user.role})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# GitHub OAuth
@router.get("/github/login")
async def github_login(request: Request):
    redirect_uri = f"{settings.APP_URL}/auth/github/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/github/callback")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.github.authorize_access_token(request)
        resp = await oauth.github.get('user', token=token)
        user_info = resp.json()
        email = user_info.get("email")
        if not email:
            # Get primary email if not public
            emails_resp = await oauth.github.get('user/emails', token=token)
            emails = emails_resp.json()
            primary_email = next((e for e in emails if e['primary']), None)
            email = primary_email['email'] if primary_email else f"{user_info['login']}@users.noreply.github.com"
    except AuthlibHTTPError:
        raise HTTPException(status_code=400, detail="GitHub OAuth failed")
    db_user = get_user_by_email(db, email)
    if not db_user:
        db_user = create_user(db, UserCreate(email=email, password=str(uuid.uuid4()), role="user"))
    access_token = create_access_token({"sub": db_user.email, "role": db_user.role})
    refresh_token = create_refresh_token({"sub": db_user.email, "role": db_user.role})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}