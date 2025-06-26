# app/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Time, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Pharmacy(Base):
    __tablename__ = 'pharmacies'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    cash_balance = Column(Float, default=0.0)

    opening_hours = relationship("OpeningHour", back_populates="pharmacy", cascade="all, delete-orphan")
    masks = relationship("Mask", back_populates="pharmacy", cascade="all, delete-orphan")


class OpeningHour(Base):
    __tablename__ = 'opening_hours'

    id = Column(Integer, primary_key=True)
    pharmacy_id = Column(Integer, ForeignKey('pharmacies.id'))
    day_of_week = Column(String, nullable=False)
    open_time = Column(Time, nullable=False)
    close_time = Column(Time, nullable=False)

    pharmacy = relationship("Pharmacy", back_populates="opening_hours")


class Mask(Base):
    __tablename__ = 'masks'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    pharmacy_id = Column(Integer, ForeignKey('pharmacies.id'))

    pharmacy = relationship("Pharmacy", back_populates="masks")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    cash_balance = Column(Float, default=0.0)

    purchase_histories = relationship("PurchaseHistory", back_populates="user", cascade="all, delete-orphan")


class PurchaseHistory(Base):
    __tablename__ = 'purchase_histories'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    pharmacy_id = Column(Integer, ForeignKey('pharmacies.id'))
    mask_name = Column(String, nullable=False)
    transaction_amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="purchase_histories")
    pharmacy = relationship("Pharmacy")
