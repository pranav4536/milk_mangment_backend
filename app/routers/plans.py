from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta

from app.database import get_db
from app.models.customer_plan import CustomerPlan, PlanDelivery, ScheduleType, PlanDeliveryStatus
from app.models.customer import Customer
from app.schemas.customer_plan import (
    CustomerPlanCreate,
    CustomerPlanUpdate,
    CustomerPlanResponse,
    PlanDeliveryResponse,
    PlanDeliveryUpdate,
)

router = APIRouter(prefix="/api/plans", tags=["Customer Plans"])


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _generate_delivery_dates(plan: CustomerPlanCreate) -> List[date]:
    """Return list of scheduled delivery dates based on plan settings."""
    dates: List[date] = []
    start = plan.start_date
    end = plan.end_date  # may be None

    if plan.schedule_type == ScheduleType.daily:
        if not end:
            # Default: generate 90 days ahead if no end_date
            end = start + timedelta(days=90)
        current = start
        while current <= end:
            dates.append(current)
            current += timedelta(days=1)

    elif plan.schedule_type == ScheduleType.alternate_days:
        if not end:
            end = start + timedelta(days=90)
        current = start
        while current <= end:
            dates.append(current)
            current += timedelta(days=2)

    elif plan.schedule_type == ScheduleType.monthly:
        # Deliver once per month on the same day-of-month as start_date
        if not end:
            end = start + timedelta(days=365)
        current = start
        while current <= end:
            dates.append(current)
            # Move to next month (same day)
            month = current.month + 1
            year = current.year
            if month > 12:
                month = 1
                year += 1
            day = min(current.day, _days_in_month(year, month))
            current = current.replace(year=year, month=month, day=day)

    elif plan.schedule_type == ScheduleType.custom_dates:
        if plan.custom_dates:
            raw = [d.strip() for d in plan.custom_dates.split(",") if d.strip()]
            for raw_date in raw:
                try:
                    dates.append(date.fromisoformat(raw_date))
                except ValueError:
                    pass  # skip badly formatted dates

    return sorted(set(dates))


def _days_in_month(year: int, month: int) -> int:
    import calendar
    return calendar.monthrange(year, month)[1]


# ─── Create plan ──────────────────────────────────────────────────────────────

@router.post("/", response_model=CustomerPlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(plan: CustomerPlanCreate, db: Session = Depends(get_db)):
    # Ensure the customer exists
    customer = db.query(Customer).filter(Customer.customer_id == plan.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db_plan = CustomerPlan(**plan.model_dump())
    db.add(db_plan)
    db.flush()  # get plan_id before committing

    # Auto-generate PlanDelivery rows
    delivery_dates = _generate_delivery_dates(plan)
    for d in delivery_dates:
        pd = PlanDelivery(
            plan_id=db_plan.plan_id,
            customer_id=plan.customer_id,
            scheduled_date=d,
            status=PlanDeliveryStatus.pending,
        )
        db.add(pd)

    db.commit()
    db.refresh(db_plan)
    return db_plan


# ─── List plans ───────────────────────────────────────────────────────────────

@router.get("/", response_model=List[CustomerPlanResponse])
def list_plans(
    customer_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    schedule_type: Optional[ScheduleType] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(CustomerPlan)
    if customer_id is not None:
        query = query.filter(CustomerPlan.customer_id == customer_id)
    if is_active is not None:
        query = query.filter(CustomerPlan.is_active == is_active)
    if schedule_type:
        query = query.filter(CustomerPlan.schedule_type == schedule_type)
    return query.offset(skip).limit(limit).all()


# ─── Get plan by ID ───────────────────────────────────────────────────────────

@router.get("/{plan_id}", response_model=CustomerPlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(CustomerPlan).filter(CustomerPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


# ─── Update plan ──────────────────────────────────────────────────────────────

@router.put("/{plan_id}", response_model=CustomerPlanResponse)
def update_plan(plan_id: int, payload: CustomerPlanUpdate, db: Session = Depends(get_db)):
    plan = db.query(CustomerPlan).filter(CustomerPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan


# ─── Delete plan ──────────────────────────────────────────────────────────────

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(CustomerPlan).filter(CustomerPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()


# ─── Customer's plans ─────────────────────────────────────────────────────────

@router.get("/customer/{customer_id}", response_model=List[CustomerPlanResponse])
def get_customer_plans(customer_id: int, db: Session = Depends(get_db)):
    return db.query(CustomerPlan).filter(CustomerPlan.customer_id == customer_id).all()


# ─── Scheduled deliveries for a plan ─────────────────────────────────────────

@router.get("/{plan_id}/deliveries", response_model=List[PlanDeliveryResponse])
def get_plan_deliveries(
    plan_id: int,
    status: Optional[PlanDeliveryStatus] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    plan = db.query(CustomerPlan).filter(CustomerPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    query = db.query(PlanDelivery).filter(PlanDelivery.plan_id == plan_id)
    if status:
        query = query.filter(PlanDelivery.status == status)
    if from_date:
        query = query.filter(PlanDelivery.scheduled_date >= from_date)
    if to_date:
        query = query.filter(PlanDelivery.scheduled_date <= to_date)
    return query.order_by(PlanDelivery.scheduled_date).all()


# ─── All deliveries on a given date (across all customers) ───────────────────

@router.get("/deliveries/date/{delivery_date}", response_model=List[PlanDeliveryResponse])
def get_deliveries_by_date(
    delivery_date: date,
    status: Optional[PlanDeliveryStatus] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(PlanDelivery).filter(PlanDelivery.scheduled_date == delivery_date)
    if status:
        query = query.filter(PlanDelivery.status == status)
    return query.order_by(PlanDelivery.customer_id).all()


# ─── Update a single scheduled delivery status ────────────────────────────────

@router.put("/deliveries/{delivery_row_id}", response_model=PlanDeliveryResponse)
def update_plan_delivery(
    delivery_row_id: int,
    payload: PlanDeliveryUpdate,
    db: Session = Depends(get_db),
):
    record = db.query(PlanDelivery).filter(PlanDelivery.id == delivery_row_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Plan delivery record not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record
