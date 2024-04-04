import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dadata import Dadata
import requests
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

SECRET_AUTH = os.environ.get("SECRET_AUTH")

SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = int(os.environ.get("SMTP_PORT"))
SMTP_SSL = os.environ.get("SMTP_SSL")
SMTP_LOGIN = os.environ.get("SMTP_LOGIN")
SMTP_PASS = os.environ.get("SMTP_PASS")


class Settings(BaseModel):
    authjwt_secret_key: str = SECRET_AUTH
    authjwt_algorithm: str = "HS256"
    authjwt_access_token_expires: int = 60 * 60 * 72  # default 15 minute
    authjwt_refresh_token_expires: int = 31000000  # default 30 days


def send_email(recipient_email, subject, message):
    msg = MIMEMultipart()
    msg['From'] = SMTP_LOGIN
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_LOGIN, SMTP_PASS)
        smtp.send_message(msg)
