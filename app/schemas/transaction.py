from pydantic import BaseModel, ConfigDict, model_validator
from typing import Optional
from datetime import date, datetime
from enum import Enum


# ─── Shared enums ─────────────────────────────────────────────────────────────

class PaymentStatus(str, Enum):
    paid = "Paid"
    partial = "Partial"
    pending = "Pending"


# ══════════════════════════════════════════════════════════════════════════════
# Customer Transaction
# ══════════════════════════════════════════════════════════════════════════════

class CustomerPaymentMode(str, Enum):
    online = "online"
    cash = "cash"


class CustomerTransactionBase(BaseModel):
    customer_id: int
    date: date
    total_amount: float
    paid_amount: float = 0.0
    payment_mode: CustomerPaymentMode
    notes: Optional[str] = None


class CustomerTransactionCreate(CustomerTransactionBase):
    """pending_amount and status are auto-derived from total_amount and paid_amount."""

    @model_validator(mode="before")
    @classmethod
    def _validate(cls, values):
        total = float(values.get("total_amount", 0) or 0)
        paid = float(values.get("paid_amount", 0) or 0)
        if paid > total:
            raise ValueError("paid_amount cannot exceed total_amount")
        return values


class CustomerTransactionUpdate(BaseModel):
    date: Optional[date] = None
    total_amount: Optional[float] = None
    paid_amount: Optional[float] = None
    payment_mode: Optional[CustomerPaymentMode] = None
    status: Optional[PaymentStatus] = None
    notes: Optional[str] = None


class CustomerTransactionResponse(CustomerTransactionBase):
    transaction_id: int
    pending_amount: float
    status: PaymentStatus
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════════════════════════════════════
# Vendor Transaction
# ══════════════════════════════════════════════════════════════════════════════

class VendorTransactionBase(BaseModel):
    vendor_id: int
    date: date
    milk_qty: float
    rate: float
    paid_amount: float = 0.0
    notes: Optional[str] = None


class VendorTransactionCreate(VendorTransactionBase):
    """total_amount and due_amount are auto-derived."""

    @model_validator(mode="before")
    @classmethod
    def _validate(cls, values):
        qty = float(values.get("milk_qty", 0) or 0)
        rate = float(values.get("rate", 0) or 0)
        paid = float(values.get("paid_amount", 0) or 0)
        total = qty * rate
        if paid > total:
            raise ValueError("paid_amount cannot exceed total_amount (milk_qty × rate)")
        return values


class VendorTransactionUpdate(BaseModel):
    date: Optional[date] = None
    milk_qty: Optional[float] = None
    rate: Optional[float] = None
    paid_amount: Optional[float] = None
    status: Optional[PaymentStatus] = None
    notes: Optional[str] = None


class VendorTransactionResponse(VendorTransactionBase):
    transaction_id: int
    total_amount: float
    due_amount: float
    status: PaymentStatus
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
