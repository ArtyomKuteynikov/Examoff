import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, Boolean, DateTime, Float
from sqlalchemy.orm import relationship

from config.database import Base


class Order(Base):
    __tablename__ = 'order'

    TYPES = {
        'courier': 'Доставка',
        'self': 'Самовывоз'
    }

    STATUSES = {
        0: 'Создан',
        1: 'Принят',
        2: 'Отменён',
        3: 'Готов',
        4: 'В пути',
        5: 'Выполнен'
    }

    DELIVERY_TYPES = {
        'asap': 'Заказ на ближайшее время',
        'time': 'Заказ на определенное время'
    }

    PAYMENT_METHOD = {
        'cache': 'Оплата наличными при получении',
        'card': 'Оплата картой при получении',
        'online': 'Оплата картой онлайн'
    }

    id = Column(Integer, primary_key=True)
    uuid = Column(String(128), default=lambda: str(uuid.uuid4()))
    courier_id = Column(Integer, ForeignKey('courier.id'), nullable=True)
    type = Column(String(32))
    name = Column(String(64))
    phone = Column(String(32))
    address = Column(String(1024))
    lon = Column(Float)
    lat = Column(Float)
    apartment = Column(String(16))
    flat = Column(String(16))
    code = Column(String(32))
    gate = Column(String(16))
    comment = Column(String(1024))
    delivery_type = Column(String(32))
    time = Column(DateTime, nullable=True)
    payment_method = Column(String(32))
    paid = Column(Boolean, default=False)
    promo = Column(String(32), nullable=True)
    status = Column(Integer, default=0)
    delivery_price = Column(Float, default=0, nullable=True)
    approx_finishing_time = Column(DateTime, nullable=True)
    cancellation_reason = Column(String(256), nullable=True)
    created = Column(DateTime, nullable=False)
    accepted = Column(DateTime, nullable=True)
    ready = Column(DateTime, nullable=True)
    delivery_start = Column(DateTime, nullable=True)
    finished = Column(DateTime, nullable=True)
    canceled = Column(DateTime, nullable=True)
    updated = Column(DateTime, nullable=False)


class OrderRate(Base):
    __tablename__ = 'order_rate'

    id = Column(Integer, primary_key=True)
    rate = Column(Integer)
    comment = Column(String(1024), nullable=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    created = Column(DateTime, nullable=False)


class DeliveryRate(Base):
    __tablename__ = 'delivery_rate'

    id = Column(Integer, primary_key=True)
    rate = Column(Integer)
    comment = Column(String(1024), nullable=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    created = Column(DateTime, nullable=False)


class OrderItem(Base):
    __tablename__ = 'order_item'

    id = Column(Integer, primary_key=True)
    name = Column(String(512))
    price = Column(Float, default=0)
    quantity = Column(Float, default=1)
    order_id = Column(Integer, ForeignKey('order.id'))
    external_id = Column(Integer, nullable=True)
