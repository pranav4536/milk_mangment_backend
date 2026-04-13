from sqlalchemy import (
    Column, Integer, Float, Date, DateTime, Boolean,
    String, Text, Enum as SAEnum, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ScheduleType(str, enum.Enum):
    daily = "daily"
    alternate_days = "alternate_days"
    monthly = "monthly"
    custom_dates = "custom_dates"


class PlanDeliveryStatus(str, enum.Enum):
    pending = "pending"
    delivered = "delivered"
    skipped = "skipped"


class CustomerPlan(Base):
    __tablename__ = "customer_plans"

    plan_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    schedule_type = Column(SAEnum(ScheduleType), nullable=False)
    quantity_per_delivery = Column(Float, nullable=False)   # litres per delivery
    price_per_litre = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    custom_dates = Column(Text, nullable=True)              # comma-separated dates e.g. "2026-04-01,2026-04-15"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", backref="plans")
    deliveries = relationship("PlanDelivery", back_populates="plan", cascade="all, delete-orphan")


class PlanDelivery(Base):
    __tablename__ = "plan_deliveries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(
        Integer,
        ForeignKey("customer_plans.plan_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scheduled_date = Column(Date, nullable=False, index=True)
    status = Column(SAEnum(PlanDeliveryStatus), nullable=False, default=PlanDeliveryStatus.pending)
    delivery_id = Column(Integer, nullable=True)            # FK to deliveries.delivery_id once fulfilled

    plan = relationship("CustomerPlan", back_populates="deliveries")
    customer = relationship("Customer", backref="plan_deliveries")
