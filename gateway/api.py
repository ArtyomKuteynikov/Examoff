from dotenv import load_dotenv
from redis import asyncio as aioredis
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi_pagination import add_pagination
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from gateway.config.database import init_db, get_db
from gateway.config.main import Settings
from gateway.chat.router import router as router_chat
from gateway.db.messages.repo import MessageRepo
load_dotenv()

app = FastAPI(
    title="Examoff",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)

app.include_router(router_chat)

add_pagination(app)


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def auth_jwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.on_event("startup")
async def startup_event():
    await init_db()
    global redis_pool
    redis = aioredis.from_url("redis://127.0.0.1:6379",
                              encoding="utf8", decode_responses=True)
    redis_pool = redis
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@app.on_event("shutdown")
async def shutdown_event():
    global redis_pool
    await redis_pool.close()


@app.get("/")
async def root(session: AsyncSession = Depends(get_db)):

    repo = MessageRepo(session=session)
    a = await repo.get_all()
    return {"message": "Hello World"}
