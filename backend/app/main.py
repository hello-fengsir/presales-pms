"""售前CRM v3 — FastAPI application with PostgreSQL + Redis."""
from contextlib import asynccontextmanager
import time
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.modules.presales.database import init_db as presales_init_db, engine, Base
from app.modules.presales.cache import get_redis
from app.modules.presales.router import router as presales_router
from app.modules.auth.router import router as auth_router
from app.modules.presales.routers.api_keys import router as apikey_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Wait for DB to be ready (PostgreSQL startup can take a few seconds)
    for attempt in range(20):
        try:
            with engine.connect() as conn:
                pass
            break
        except Exception:
            if attempt < 19:
                await asyncio.sleep(2)
    presales_init_db()
    # Test Redis connection
    r = get_redis()
    if r:
        try:
            r.ping()
            print("✅ Redis connected")
        except Exception:
            print("⚠️  Redis unavailable — caching disabled")
    yield


app = FastAPI(
    title="售前CRM系统 v3",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok", "system": "售前CRM v3", "version": "3.0.0"}


app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(apikey_router, prefix="/api/v1/presales")
app.include_router(presales_router)
