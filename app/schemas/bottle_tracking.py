from pydantic import BaseModel, ConfigDict
from typing import Optional


class BottleTrackingBase(BaseModel):
    customer_id: int
    total_given: Optional[int] = 0
    total_returned: Optional[int] = 0
    pending: Optional[int] = 0


class BottleTrackingCreate(BottleTrackingBase):
    pass


class BottleTrackingUpdate(BaseModel):
    total_given: Optional[int] = None
    total_returned: Optional[int] = None
    pending: Optional[int] = None


class BottleTrackingResponse(BottleTrackingBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BottleSummaryResponse(BaseModel):
    total_given: int
    total_returned: int
    total_pending: int
