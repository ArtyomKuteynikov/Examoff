import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel


class SignIn(BaseModel):
    email: str
    password: str


class SignUp(BaseModel):
    name: str
    surname: str
    phone: str
    email: str
    password: str


class SendEmail(BaseModel):
    email: str


class EmailOTP(BaseModel):
    email: str
    code: int


class NewPassword(BaseModel):
    new_password: str
    confirm_password: str
