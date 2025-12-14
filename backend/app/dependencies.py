from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.crud.user import get_user_by_email
from app.schemas.user import TokenData
from app.core.security import oauth2_scheme, redis_client
from app.core.config import settings
import jwt
from pydantic import ValidationError
from fastapi_limiter.depends import RateLimiter

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, role=payload.get("role"), jti=payload.get("jti"))
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValidationError):
        raise credentials_exception
    if redis_client.get(token_data.jti):
        raise credentials_exception
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

def require_role(roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Rate limiter function
def login_rate_limiter():
    return Depends(RateLimiter(times=5, seconds=60))