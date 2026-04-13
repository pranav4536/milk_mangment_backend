from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class MilkCollectionBase(BaseModel):
    vendor_id: int
    date: date
    quantity: float
    price: float


class MilkCollectionCreate(MilkCollectionBase):
    pass


class MilkCollectionUpdate(BaseModel):
    vendor_id: Optional[int] = None
    date: Optional[date] = None
    quantity: Optional[float] = None
    price: Optional[float] = None


class MilkCollectionResponse(MilkCollectionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
