import datetime
import random
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
from gateway.config.main import Settings, send_email
from gateway.chat.router import router as router_chat
from gateway.db.chats.repo import ChatRepo
from gateway.db.messages.repo import MessageRepo
from gateway.schemas.message import MessageInCreationSchema
from gateway.schemas.auth import SignUp, SignIn, NewPassword, EmailOTP, EditPassword
from gateway.db.auth.models import Customer, Subscriptions

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
        email=user_data.email,
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


@app.post("/v1/verify-email-otp", tags=['Account'])
async def verify_email_otp(data: EmailOTP, Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    global redis_pool
    setted_otp = await redis_pool.get(f"email:otp:{data.email}")
    if setted_otp == str(data.code):
        user = await session.execute(
            select(Customer).where((Customer.email == data.email))
        )
        user = user.fetchone()
        if user:
            access_token = Authorize.create_access_token(subject=user[0].id)
            return {
                'access_token': access_token,
                'customer_id': user.id
            }
        raise HTTPException(status_code=404, detail="email_not_found")
    else:
        raise HTTPException(status_code=404, detail="email_code_not_found")


@app.put('/v1/set-password', tags=['Account'])
async def set_new_password(data: NewPassword, Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    if data.confirm_password == data.new_password:
        user = await session.execute(
            select(Customer).where((Customer.id == current_user))
        )
        user = user.fetchone()
        if user:
            user[0].get_password_hash(data.new_password)
            await session.commit()
            return {'result': True}
        raise HTTPException(status_code=404, detail='user_not_found')
    raise HTTPException(status_code=400, detail='different_values')


@app.get("/v1/reset-password", tags=['Account'])
async def reset_password(email: str, session: AsyncSession = Depends(get_db)):
    user = await session.execute(
        select(Customer).where((Customer.email == email))
    )
    user = user.first()
    global redis_pool
    if user:
        otp = random.randint(100000, 999999)
        await redis_pool.set(f"email:otp:{email}", otp, ex=600)
        msg_body = f'''Здравствуйте, {user[0].name}!
Вы запросили сброс пароля. Пожалуйста, подтвердите email:
Ваш код подтверждения: {otp}'''
        try:
            send_email(email, 'Email confirmation', msg_body)
            return {'result': True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return {'result': False}


@app.get('/v1/profile', tags=['Account'])
async def profile(Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = await session.execute(
        select(Customer).where((Customer.id == current_user))
    )
    user = user.fetchone()
    subscriptions = await session.execute(
        select(Subscriptions).where((Subscriptions.customer_id == current_user)).order_by('end')
    )
    subscriptions = subscriptions.fetchall()
    # TODO: count invitations
    if user:
        return {'profile': {
            'email': user[0].email,
            'auto_payment': user[0].auto_payments,
            'tg_auth': False,
            'tokens': user[0].tokens,
            'subscription': datetime.datetime.now() < subscriptions[-1][0].end if subscriptions else False,
            'until': subscriptions[-1][0].end if subscriptions else None,
            'invite_code': user[0].invite_code,
            'invitations': 10
        }}
    raise HTTPException(status_code=404, detail='user_not_found')


@app.put('/v1/edit-password', tags=['Account'])
async def set_new_password(data: EditPassword, Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    if data.confirm_password == data.new_password:
        user = await session.execute(
            select(Customer).where((Customer.id == current_user))
        )
        user = user.fetchone()
        if user and user[0].verify_password(data.old_password):
            user[0].get_password_hash(data.new_password)
            await session.commit()
            return {'result': True}
        raise HTTPException(status_code=404, detail='user_not_found')
    raise HTTPException(status_code=400, detail='different_values')


@app.put('/v1/edit-email', tags=['Account'])
async def edit_email(email: str, Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = await session.execute(
        select(Customer).where((Customer.id == current_user))
    )
    user = user.fetchone()
    if user:
        user[0].email = email
        await session.commit()
    raise HTTPException(status_code=404, detail='user_not_found')
