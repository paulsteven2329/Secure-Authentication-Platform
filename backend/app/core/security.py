from datetime import datetime, timedelta
from typing import Optional
import jwt
import uuid
from redis import Redis
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer

redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)  # <-- Fixed: single 'r'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4()), "scope": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def revoke_token(jti: str, exp: int):
    ex = exp - int(datetime.utcnow().timestamp())
    if ex > 0:
        redis_client.set(jti, "revoked", ex=ex)