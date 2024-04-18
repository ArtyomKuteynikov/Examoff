import uuid
from datetime import datetime

from sqlalchemy import Boolean, Enum, Text, DateTime
from sqlalchemy import Table, Column, Integer, String, ForeignKey, REAL
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

from config.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Customer(Base):
    __tablename__ = "customer"
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(50), nullable=True)
    surname: str = Column(String(50), nullable=True)
    phone: str = Column(String(50), nullable=True)
    email: str = Column(String(50), nullable=False)
    password: str = Column(String(length=1024), nullable=False)
    confirmed: bool = Column(Boolean, default=False, nullable=False)
    tokens: int = Column(Integer, default=0)
    invite_code: str = Column(String(50), defalt=uuid.uuid4)
    referer: int = Column(Integer, default=0, nullable=True)
    show: bool = Column(Boolean, default=True, nullable=False)
    active: bool = Column(Boolean, default=True, nullable=False)

    def get_password_hash(self, password):
        self.password = pwd_context.hash(password)
        return pwd_context.hash(password)

    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.password)