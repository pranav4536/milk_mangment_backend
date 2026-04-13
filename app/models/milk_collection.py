from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class MilkCollection(Base):
    __tablename__ = "milk_collection"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    quantity = Column(Float, nullable=False)  # litres
    price = Column(Float, nullable=False)     # per litre or total

    vendor = relationship("Vendor", backref="collections")
