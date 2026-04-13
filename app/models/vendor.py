from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    vendor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    milk_type = Column(String(100), nullable=True)
    capacity = Column(Float, nullable=True)  # litres per day
