from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    lat = Column(Float, nullable=True)         # latitude
    long = Column(Float, nullable=True)        # longitude
    milk_type = Column(String(100), nullable=True)
    daily_qty = Column(Float, nullable=True)   # daily quantity in litres
