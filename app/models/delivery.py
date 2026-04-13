from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Delivery(Base):
    __tablename__ = "deliveries"

    delivery_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    quantity = Column(Float, nullable=False)          # litres delivered
    price = Column(Float, nullable=False)             # total price
    bottles_given = Column(Integer, default=0)
    bottles_returned = Column(Integer, default=0)

    customer = relationship("Customer", backref="deliveries")
