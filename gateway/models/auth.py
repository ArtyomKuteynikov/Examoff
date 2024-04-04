from datetime import datetime

from sqlalchemy import Boolean, Enum, Text, DateTime, func
from sqlalchemy import Table, Column, Integer, String, ForeignKey, REAL
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

from config.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Courier(Base):
    __tablename__ = 'courier'
    id: int = Column(Integer, primary_key=True, index=True)
    login: str = Column(String(32))
    password: str = Column(String(16))
    email: str = Column(String(64))
    phone: str = Column(String(32))
    name: str = Column(String(64))
    surname: str = Column(String(64))
    show: bool = Column(Boolean, default=True)
    type: int = Column(Integer)
    gos_num: str = Column(String(32), nullable=True)
    vin: str = Column(String(128), nullable=True)
    brand: str = Column(String(32), nullable=True)
    model: str = Column(String(32), nullable=True)
    color: str = Column(String(32), nullable=True)

    def verify_password(self, plain_password):
        return plain_password == self.password


class OrderMessages(Base):
    __tablename__ = "order_messages"

    id = Column(Integer, primary_key=True, index=True)
    author = Column(Integer, nullable=False)
    message = Column(String(1024), nullable=False)
    order_id = Column(Integer, ForeignKey("order.id"))
    manager_id = Column(Integer, nullable=True)
    created = Column(DateTime, default=func.now(), nullable=False)
    read = Column(Boolean, default=False)
