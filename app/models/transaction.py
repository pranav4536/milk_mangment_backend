"""
Two separate transaction tables:
  - customer_transactions : tracks payments made by customers
  - vendor_transactions   : tracks milk purchases from vendors
"""
from sqlalchemy import Column, Integer, Float, Date, DateTime, String, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


# ─── Shared enums ─────────────────────────────────────────────────────────────

class PaymentStatus(str, enum.Enum):
    paid = "Paid"
    partial = "Partial"
    pending = "Pending"


# ─── Customer Transaction ─────────────────────────────────────────────────────

class CustomerPaymentMode(str, enum.Enum):
    online = "online"
    cash = "cash"


class CustomerTransaction(Base):
    __tablename__ = "customer_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date = Column(Date, nullable=False)
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, nullable=False, default=0.0)
    pending_amount = Column(Float, nullable=False, default=0.0)   # stored for quick queries
    payment_mode = Column(SAEnum(CustomerPaymentMode), nullable=False)
    status = Column(SAEnum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", backref="customer_transactions")


# ─── Vendor Transaction ───────────────────────────────────────────────────────

class VendorTransaction(Base):
    __tablename__ = "vendor_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vendor_id = Column(
        Integer,
        ForeignKey("vendors.vendor_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date = Column(Date, nullable=False)
    milk_qty = Column(Float, nullable=False)          # litres collected
    rate = Column(Float, nullable=False)              # price per litre
    total_amount = Column(Float, nullable=False)      # milk_qty × rate (stored for quick queries)
    paid_amount = Column(Float, nullable=False, default=0.0)
    due_amount = Column(Float, nullable=False, default=0.0)       # total_amount - paid_amount
    status = Column(SAEnum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vendor = relationship("Vendor", backref="vendor_transactions")
