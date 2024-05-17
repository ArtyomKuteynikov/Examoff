import datetime
import hashlib
import hmac
import os
import random
import uuid
import secrets
import string
from typing import Annotated

import requests
from dotenv import load_dotenv
from fastapi_sso import GoogleSSO
from redis import asyncio as aioredis
from fastapi import UploadFile, Query
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
from starlette.responses import HTMLResponse, PlainTextResponse
from starlette.staticfiles import StaticFiles
from gateway.config.database import init_db, get_db, async_session_maker
from gateway.config.main import Settings, send_email
from gateway.chat.router import router as router_chat
from gateway.audio.router import router as router_audio
from gateway.db.chats.repo import ChatRepo
from gateway.db.files.models import File
from gateway.db.files.repo import FileRepo
from gateway.db.messages.repo import MessageRepo
from gateway.schemas.file import FileSchema
from gateway.schemas.message import MessageInCreationSchema
from gateway.schemas.auth import SignUp, SignIn, NewPassword, EmailOTP, EditPassword
from gateway.db.auth.models import Customer, Subscriptions
from fastapi import FastAPI, HTTPException, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

load_dotenv()
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "CLIENT_ID is empty")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "CLIENT_SECRET is empty")
GOOGLE_REDIRECT_URL = os.environ.get("GOOGLE_REDIRECT_URL", "GOOGLE_REDIRECT_URL is empty")
BOT_TOKEN_HASH = hashlib.sha256(os.environ['BOT_TOKEN'].encode())
google_sso = GoogleSSO(CLIENT_ID, CLIENT_SECRET, GOOGLE_REDIRECT_URL)

app = FastAPI(
    title="Examoff",
)

app.mount("/gateway/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/yandex", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request, name="item.html",
    )


@app.get("/telegram", response_class=HTMLResponse)
async def telegram(request: Request):
    return templates.TemplateResponse(
        request=request, name="tg.html",
    )


@app.get("/auth/telegram-callback", response_class=HTMLResponse)
async def telegram_auth(
        request: Request,
        user_id: Annotated[int, Query(alias='id')],
        query_hash: Annotated[str, Query(alias='hash')],
        next_url: Annotated[str, Query(alias='next')] = '/',
        session: AsyncSession = Depends(get_db),
        Authorize: AuthJWT = Depends()
):
    params = request.query_params.items()
    data_check_string = '\n'.join(sorted(f'{x}={y}' for x, y in params if x not in ('hash', 'next')))
    computed_hash = hmac.new(BOT_TOKEN_HASH.digest(), data_check_string.encode(), 'sha256').hexdigest()
    is_correct = hmac.compare_digest(computed_hash, query_hash)
    if not is_correct:
        return PlainTextResponse('Authorization failed. Please try again', status_code=401)
    username = '@' + str(request.query_params['username'])
    # Проверка на наличии пользователя
    query = select(Customer).where((Customer.email == username))
    result = await session.execute(query)
    user = result.first()
    if user:
        access_token = Authorize.create_access_token(subject=user[0].id)
        html_page = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
        </head>
        <body>

        </body>
        <script>
        window.onload = () => {{
            window.opener.postMessage('{access_token}', '*')
            window.close()
            }}
        </script>
        </html>
        """
        return html_page

    # Регистрация
    user = Customer(
        email=username,
    )
    session.add(user)
    # await session.commit()
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    user.get_password_hash(password)
    await session.commit()

    access_token = Authorize.create_access_token(subject=user.id)
    html_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    </head>
    <body>

    </body>
    <script>
    window.onload = () => {{
        window.opener.postMessage('{access_token}', '*')
        window.close()
        }}
    </script>
    </html>
    """
    return html_page


@app.get("/yandex/auth")
async def yandex_auth(yandex_token: str, session: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    response = requests.get(
        url='https://login.yandex.ru/info',
        params={
            'oauth_token': yandex_token
        }
    )
    response = response.json()
    yandex_email = response['default_email']

    # Проверка на наличии пользователя
    query = select(Customer).where((Customer.email == yandex_email))
    result = await session.execute(query)
    user = result.first()
    if user:
        access_token = Authorize.create_access_token(subject=user[0].id)
        return {
            'access_token': access_token,
            'customer_id': user[0].id
        }

    # Регистрация
    user = Customer(
        email=yandex_email,
    )
    session.add(user)
    # await session.commit()
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    user.get_password_hash(password)
    await session.commit()

    access_token = Authorize.create_access_token(subject=user.id)
    return {
        'access_token': access_token,
        'customer_id': user.id
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)

app.include_router(router_chat)
app.include_router(router_audio)

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


async def check_user(email: str, session: AsyncSession):
    query = select(Customer).where((Customer.email == email))
    result = await session.execute(query)
    user = result.first()
    if user:
        return True
    return False


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
    # await session.commit()
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


@app.get("/google/login")
async def google_login():
    print(CLIENT_ID, CLIENT_SECRET, GOOGLE_REDIRECT_URL)
    with google_sso:
        return await google_sso.get_login_redirect()


@app.get("/google/callback", response_class=HTMLResponse)
async def google_callback(request: Request, session: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    with google_sso:
        google_user = await google_sso.verify_and_process(request)

    # Проверка на наличии пользователя
    query = select(Customer).where((Customer.email == google_user.email))
    result = await session.execute(query)
    user = result.first()
    if user:
        access_token = Authorize.create_access_token(subject=user[0].id)
        html_page = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
        </head>
        <body>
        
        </body>
        <script>
        window.onload = () => {{
            window.opener.postMessage('{access_token}', '*')
            window.close()
            }}
        </script>
        </html>
        """
        return html_page

    # Регистрация
    user = Customer(
        email=google_user.email,
    )
    session.add(user)
    # await session.commit()
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    user.get_password_hash(password)
    await session.commit()

    access_token = Authorize.create_access_token(subject=user.id)
    html_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    </head>
    <body>

    </body>
    <script>
    window.onload = () => {{
        window.opener.postMessage('{access_token}', '*')
        window.close()
        }}
    </script>
    </html>
    """
    return html_page


@app.post("/v1/signin", tags=['Account'])
async def signin(data: SignIn, Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    user = await authenticate_user(data.email, data.password, session)
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
        user = user.first()
        if user:
            access_token = Authorize.create_access_token(subject=user[0].id)
            return {
                'access_token': access_token,
                'customer_id': user[0].id
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
        user = user.first()
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
        msg_body = f'''Здравствуйте!
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
    user = await session.execute(
        select(Customer).where((Customer.id == current_user))
    )
    user = user.fetchone()
    if user and user[0].verify_password(data.old_password):
        user[0].get_password_hash(data.new_password)
        await session.commit()
        return {'result': True}
    raise HTTPException(status_code=404, detail='user_not_found')


@app.put('/v1/edit-email', tags=['Account'])
async def edit_email(email: str, Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = await session.execute(
        select(Customer).where((Customer.id == current_user))
    )
    user = user.fetchone()
    global redis_pool
    if await check_user(email, session):
        raise HTTPException(status_code=403, detail="user_not_allowed")
    if user:
        otp = random.randint(100000, 999999)
        await redis_pool.set(f"email:otp:{user[0].email}", otp, ex=600)
        await redis_pool.set(f"email:new:{user[0].email}", email, ex=600)
        msg_body = f'''Здравствуйте!
Вы запросили изменение email. Пожалуйста, подтвердите новый email:
Ваш код подтверждения: {otp}'''
        try:
            send_email(email, 'Email confirmation', msg_body)
            return {'result': True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return {'result': False}


@app.put('/v1/edit-email-confirm', tags=['Account'])
async def edit_email(code: int, Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = await session.execute(
        select(Customer).where((Customer.id == current_user))
    )
    user = user.fetchone()
    global redis_pool
    if user:
        setted_otp = await redis_pool.get(f"email:otp:{user[0].email}")
        if setted_otp == str(code):
            email = await redis_pool.get(f"email:new:{user[0].email}")
            user[0].email = email
            await session.commit()
            return {'result': True}
        raise HTTPException(status_code=404, detail="email_not_found")
    else:
        raise HTTPException(status_code=404, detail="email_code_not_found")


@app.get("/messages", responses={
    200: {
        "description": "Successful Response.",
        "content": {
            "application/json": {
                "example": {
                    "messages": [
                        {
                            "id": 349,
                            "chat_id": 25,
                            "text": "Привет! Я - Examoff, твой верный компаньон в образовательном путешествии.\n",
                            "sender_id": 1,
                            "created_at": "2024-04-24T18:48:45.796985Z",
                            "response_specific_state": 'null'
                        },
                        {
                            "id": 352,
                            "chat_id": 25,
                            "text": "Привет.",
                            "sender_id": 3,
                            "created_at": "2024-04-24T18:48:45.796000Z",
                            "response_specific_state": 'null'
                        }
                    ]
                }
            }
        }
    }}
         )
async def get_user_messages_by_chat(
        chat_id: int,
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_db)
):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = await session.execute(
        select(Customer).where((Customer.id == current_user))
    )
    user = user.fetchone()
    if user:
        chat_repo = ChatRepo(session)
        chats = await chat_repo.get_chats_by_attributes({'user_owner_id': user[0].id})
        result = list(filter(lambda chat: (chat.id == chat_id), chats))
        if result:
            message_repo = MessageRepo(session)
            messages = await message_repo.get_messages_by_attributes({'chat_id': chat_id})
            return {'messages': messages}

    raise HTTPException(status_code=403, detail="Auth failed.")


@app.get("/files/{file_id}", response_class=FileResponse)
async def download_file(file_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Download a file by its UUID.

    This endpoint will retrieve the file if the file with the given UUID exists and the user has permissions to access it.
    """
    file_repo = FileRepo(db)
    file_data: FileSchema = await file_repo.get_file_by_id(file_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = f"files/{file_data.id}.docx"
    try:
        return FileResponse(path=file_path, filename=str(file_data.id) + '.docx', media_type='application/octet-stream')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found on server")


@app.get("/files/", response_class=FileResponse)
async def get_file_id_by_chat(chat_id: int, db: AsyncSession = Depends(get_db)):
    """
    Download a file by its UUID.

    This endpoint will retrieve the file if the file with the given UUID exists and the user has permissions to access it.
    """
    file_repo = FileRepo(db)
    file_data: FileSchema = await file_repo.get_file_by_chat_id(chat_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = f"files/{file_data.id}.docx"
    try:
        return FileResponse(path=file_path, filename=str(file_data.id) + '.docx', media_type='application/octet-stream')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found on server")


@app.get("/user_file/", response_class=FileResponse)
async def get_user_file_by_chat_and_file_name(file_path: str, file_name):
    """
    Pass
    """
    try:
        return FileResponse(path=file_path, filename=file_name, media_type='application/octet-stream')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found on server")


@app.post("/files/upload")
async def upload_file(
        chat_id: int,
        file: UploadFile,
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_db)
):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = await session.execute(
        select(Customer).where((Customer.id == current_user))
    )
    user = user.fetchone()

    if user:
        os.makedirs(f"files/user_uploads/{user[0].id}/{chat_id}", exist_ok=True)
        file_location = f"files/user_uploads/{user[0].id}/{chat_id}/"
        contents = await file.read()
        with open(file_location + file.filename, 'wb') as f:
            f.write(contents)

        async with async_session_maker() as session:
            message_in_creation = MessageInCreationSchema(
                chat_id=chat_id,
                text='',
                sender_id=user[0].id,
                file_name=file.filename,
                file_link=file_location + file.filename,
                response_specific_state='UPLOADED_FILE',
            )
            message_repo = MessageRepo(session)
            await message_repo.create_message(message_in_creation)

        return {"file_link": f"{file_location + file.filename}"}
    return {"Status": f"Didn't find user."}
