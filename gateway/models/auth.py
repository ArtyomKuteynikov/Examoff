from datetime import datetime

from sqlalchemy import Boolean, Enum, Text, DateTime, func
from sqlalchemy import Table, Column, Integer, String, ForeignKey, REAL
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

from config.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

