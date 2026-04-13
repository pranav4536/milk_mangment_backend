from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models.bottle_tracking import BottleTracking
from app.schemas.bottle_tracking import (
    BottleTrackingCreate,
    BottleTrackingUpdate,
    BottleTrackingResponse,
    BottleSummaryResponse,
)

router = APIRouter(prefix="/api/bottle-tracking", tags=["Bottle Tracking"])


@router.post("/", response_model=BottleTrackingResponse, status_code=status.HTTP_201_CREATED)
def create_bottle_tracking(tracking: BottleTrackingCreate, db: Session = Depends(get_db)):
    # Auto-calculate pending
    data = tracking.model_dump()
    data["pending"] = data.get("total_given", 0) - data.get("total_returned", 0)
    db_tracking = BottleTracking(**data)
    db.add(db_tracking)
    db.commit()
    db.refresh(db_tracking)
    return db_tracking


@router.get("/summary", response_model=BottleSummaryResponse)
def get_bottle_summary(db: Session = Depends(get_db)):
    result = db.query(
        func.sum(BottleTracking.total_given).label("total_given"),
        func.sum(BottleTracking.total_returned).label("total_returned"),
        func.sum(BottleTracking.pending).label("total_pending"),
    ).first()
    return {
        "total_given": result.total_given or 0,
        "total_returned": result.total_returned or 0,
        "total_pending": result.total_pending or 0,
    }


@router.get("/", response_model=List[BottleTrackingResponse])
def list_bottle_tracking(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(BottleTracking).offset(skip).limit(limit).all()


@router.get("/{customer_id}", response_model=BottleTrackingResponse)
def get_bottle_tracking(customer_id: int, db: Session = Depends(get_db)):
    record = db.query(BottleTracking).filter(BottleTracking.customer_id == customer_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Bottle tracking record not found for this customer")
    return record


@router.put("/{customer_id}", response_model=BottleTrackingResponse)
def update_bottle_tracking(customer_id: int, tracking: BottleTrackingUpdate, db: Session = Depends(get_db)):
    record = db.query(BottleTracking).filter(BottleTracking.customer_id == customer_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Bottle tracking record not found for this customer")
    for key, value in tracking.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    # Recalculate pending after update
    record.pending = record.total_given - record.total_returned
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bottle_tracking(customer_id: int, db: Session = Depends(get_db)):
    record = db.query(BottleTracking).filter(BottleTracking.customer_id == customer_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Bottle tracking record not found for this customer")
    db.delete(record)
    db.commit()
