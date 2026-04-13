from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class DeliveryBase(BaseModel):
    customer_id: int
    date: date
    quantity: float
    price: float
    bottles_given: Optional[int] = 0
    bottles_returned: Optional[int] = 0


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryUpdate(BaseModel):
    customer_id: Optional[int] = None
    date: Optional[date] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    bottles_given: Optional[int] = None
    bottles_returned: Optional[int] = None


class DeliveryResponse(DeliveryBase):
    delivery_id: int

    model_config = ConfigDict(from_attributes=True)
