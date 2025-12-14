from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, protected
from app.core.config import settings    
from redis.asyncio import from_url
from fastapi_limiter import FastAPILimiter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(protected.router, prefix="/protected")

@app.on_event("startup")
async def startup():
    redis = from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)