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
from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy import select
from gateway.config.database import init_db, get_db
from gateway.config.main import Settings
from gateway.chat.router import router as router_chat
from gateway.db.chats.repo import ChatRepo
from gateway.db.messages.repo import MessageRepo
from gateway.schemas.message import MessageInCreationSchema
from gateway.schemas.auth import SignUp, SignIn
from gateway.db.auth.models import Customer

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


def clean_phone(phone):
    return phone.replace('(', '').replace(')', '').replace('-', '').replace('+', '').replace(' ', '')


async def authenticate_user(username: str, password: str, session: AsyncSession):
    result = await session.execute(
        select(Customer).where(
            (Customer.email == username)
        )
    )
    user = result.first()
    if user and user[0].verify_password(password):
        return user[0]
    return None


async def register_user(user_data: SignUp, session: AsyncSession):
    query = select(Customer).where((Customer.email == user_data.email))
    result = await session.execute(query)
    user = result.first()
    if user:
        return None
    user = Customer(
        phone=clean_phone(user_data.phone),
        email=user_data.email,
        name=user_data.name,
        surname=user_data.surname
    )
    session.add(user)
    await session.commit()
    user.get_password_hash(user_data.password)
    await session.commit()
    return user


@app.get("/")
async def root(session: AsyncSession = Depends(get_db)):
    # Код для тестов, он не имеет смысла
    repo = ChatRepo(session=session)

    to_print = await repo.get_chat_by_id(2)
    print(f"repo.get_message_by_id = {to_print}")

    return {"message": "Hello World"}


@app.post("/v1/signin", tags=['Account'])
async def signin(data: SignIn, Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    user = await authenticate_user(data.username, data.password, session)
    if user is None:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")
    access_token = Authorize.create_access_token(subject=user.id)
    return {
        'access_token': access_token,
        'customer_id': user.id
    }


@app.post('/v1/signup', tags=['Account'])
async def signup(data: SignUp, Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    user = await register_user(data, session)
    if user is None:
        raise HTTPException(status_code=403, detail="user_not_allowed")
    return {
        'result': True
    }