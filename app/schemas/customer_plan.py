from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class ScheduleType(str, Enum):
    daily = "daily"
    alternate_days = "alternate_days"
    monthly = "monthly"
    custom_dates = "custom_dates"


class PlanDeliveryStatus(str, Enum):
    pending = "pending"
    delivered = "delivered"
    skipped = "skipped"


class CustomerPlanBase(BaseModel):
    customer_id: int
    schedule_type: ScheduleType
    quantity_per_delivery: float
    price_per_litre: float
    start_date: date
    end_date: Optional[date] = None
    custom_dates: Optional[str] = None   # comma-separated "YYYY-MM-DD,YYYY-MM-DD"
    is_active: Optional[bool] = True


class CustomerPlanCreate(CustomerPlanBase):
    pass


class CustomerPlanUpdate(BaseModel):
    schedule_type: Optional[ScheduleType] = None
    quantity_per_delivery: Optional[float] = None
    price_per_litre: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    custom_dates: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerPlanResponse(CustomerPlanBase):
    plan_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PlanDeliveryBase(BaseModel):
    plan_id: int
    customer_id: int
    scheduled_date: date
    status: PlanDeliveryStatus = PlanDeliveryStatus.pending
    delivery_id: Optional[int] = None


class PlanDeliveryUpdate(BaseModel):
    status: Optional[PlanDeliveryStatus] = None
    delivery_id: Optional[int] = None


class PlanDeliveryResponse(PlanDeliveryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
