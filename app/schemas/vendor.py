from pydantic import BaseModel, ConfigDict
from typing import Optional


class VendorBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    milk_type: Optional[str] = None
    capacity: Optional[float] = None


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    milk_type: Optional[str] = None
    capacity: Optional[float] = None


class VendorResponse(VendorBase):
    vendor_id: int

    model_config = ConfigDict(from_attributes=True)
