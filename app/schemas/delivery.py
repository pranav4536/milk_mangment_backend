from pydantic import BaseModel, ConfigDict, model_validator
from typing import Optional
from datetime import date, datetime
from enum import Enum


class PaymentStatus(str, Enum):
    paid = "Paid"
    partial = "Partial"
    pending = "Pending"


class DeliveryPaymentMode(str, Enum):
    online = "online"
    cash = "cash"
    none = "none"


class DeliveryBase(BaseModel):
    customer_id: int
    date: date
    quantity: float
    price: float
    bottles_given: Optional[int] = 0
    bottles_returned: Optional[int] = 0


class DeliveryCreate(DeliveryBase):
    """
    Accepts delivery info + optional payment details.
    pending_amount and status are auto-derived (price - paid_amount).
    """
    paid_amount: float = 0.0
    payment_mode: DeliveryPaymentMode = DeliveryPaymentMode.none
    notes: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _validate(cls, values):
        price = float(values.get("price", 0) or 0)
        paid = float(values.get("paid_amount", 0) or 0)
        if paid > price:
            raise ValueError("paid_amount cannot exceed price (total delivery amount)")
        return values


class DeliveryUpdate(BaseModel):
    customer_id: Optional[int] = None
    date: Optional[date] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    bottles_given: Optional[int] = None
    bottles_returned: Optional[int] = None
    paid_amount: Optional[float] = None
    payment_mode: Optional[DeliveryPaymentMode] = None
    status: Optional[PaymentStatus] = None
    notes: Optional[str] = None


class DeliveryResponse(DeliveryBase):
    delivery_id: int
    paid_amount: float
    pending_amount: float
    payment_mode: DeliveryPaymentMode
    status: PaymentStatus
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
