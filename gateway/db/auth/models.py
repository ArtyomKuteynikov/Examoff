import uuid
from datetime import datetime

from sqlalchemy import Boolean, Enum, Text, DateTime
from sqlalchemy import Table, Column, Integer, String, ForeignKey, REAL
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

from gateway.config.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Customer(Base):
    __tablename__ = "system_customer"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(50), nullable=True)
    surname: str = Column(String(50), nullable=True)
    phone: str = Column(String(50), nullable=True)
    email: str = Column(String(50), nullable=False)
    password: str = Column(String(length=1024), nullable=True)
    confirmed: bool = Column(Boolean, default=True, nullable=False)
    tokens: int = Column(Integer, default=0)
    invite_code: str = Column(String(50), default=uuid.uuid4().__str__)
    referer_id: int = Column(Integer, nullable=True)
    auto_payments: bool = Column(Boolean, default=False, nullable=False)
    show: bool = Column(Boolean, default=True, nullable=False)
    active: bool = Column(Boolean, default=True, nullable=False)
    created = Column(DateTime(timezone=True), default=datetime.utcnow)

    def get_password_hash(self, password):
        self.password = pwd_context.hash(password)
        return pwd_context.hash(password)

    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.password)


class Subscriptions(Base):
    __tablename__ = "system_subscriptions"

    id: int = Column(Integer, primary_key=True)
    customer_id: int = Column(Integer, ForeignKey('customer.id'), nullable=False)
    start = Column(DateTime(timezone=True))
    end = Column(DateTime(timezone=True))


class Settings(Base):
    __tablename__ = "system_settings"

    id: int = Column(Integer, primary_key=True)
    max_refers: int = Column(Integer)
    referer_tokens: int = Column(Integer)
    subscription_price: float = Column(REAL)
    token_price: float = Column(REAL)
    tokens_in_subscription: int = Column(Integer)
    text: str = Column(String(1024))


# class Transactions(Base):
#     __tablename__ = "system_transactions"
#
#     customer_id: int = Column(Integer, ForeignKey('customer.id'), nullable=False)
#     amount: float = Column(REAL)
#     type: int = Column(Integer)
#     method: int = Column(Integer)
#     tokens: int = Column(Integer)
#     paid: bool = Column(Boolean, default=False, nullable=False)
#     created = Column(DateTime(timezone=True), default=datetime.utcnow)
