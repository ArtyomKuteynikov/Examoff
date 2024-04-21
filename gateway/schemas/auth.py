import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel


class SignIn(BaseModel):
    email: str
    password: str


class SignUp(BaseModel):
    email: str
    password: str
    invite_code: str | None


class SendEmail(BaseModel):
    email: str


class EmailOTP(BaseModel):
    email: str
    code: int


class NewPassword(BaseModel):
    new_password: str
    confirm_password: str


class EditPassword(BaseModel):
    old_password: str
    new_password: str
