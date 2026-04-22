from sqlalchemy import Column, Integer, Float, Date, DateTime, String, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class PaymentStatus(str, enum.Enum):
    paid = "Paid"
    partial = "Partial"
    pending = "Pending"


class DeliveryPaymentMode(str, enum.Enum):
    online = "online"
    cash = "cash"
    none = "none"


class Delivery(Base):
    __tablename__ = "deliveries"

    delivery_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    quantity = Column(Float, nullable=False)           # litres delivered
    price = Column(Float, nullable=False)              # total price (quantity × rate)
    bottles_given = Column(Integer, default=0)
    bottles_returned = Column(Integer, default=0)

    # ── Transaction / Payment fields ──────────────────────────────────────────
    paid_amount = Column(Float, nullable=False, default=0.0)
    pending_amount = Column(Float, nullable=False, default=0.0)   # price - paid_amount
    payment_mode = Column(SAEnum(DeliveryPaymentMode), nullable=False, default=DeliveryPaymentMode.none)
    status = Column(SAEnum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", backref="deliveries")
