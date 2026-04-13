from pydantic import BaseModel, ConfigDict
from typing import Optional


class CustomerBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    lat: Optional[float] = None
    long: Optional[float] = None
    milk_type: Optional[str] = None
    daily_qty: Optional[float] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    lat: Optional[float] = None
    long: Optional[float] = None
    milk_type: Optional[str] = None
    daily_qty: Optional[float] = None


class CustomerResponse(CustomerBase):
    customer_id: int

    model_config = ConfigDict(from_attributes=True)
