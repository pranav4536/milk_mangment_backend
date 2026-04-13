from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.delivery import Delivery
from app.schemas.delivery import DeliveryCreate, DeliveryUpdate, DeliveryResponse

router = APIRouter(prefix="/api/deliveries", tags=["Deliveries"])


@router.post("/", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(delivery: DeliveryCreate, db: Session = Depends(get_db)):
    db_delivery = Delivery(**delivery.model_dump())
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    return db_delivery


@router.get("/", response_model=List[DeliveryResponse])
def list_deliveries(
    customer_id: Optional[int] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Delivery)
    if customer_id:
        query = query.filter(Delivery.customer_id == customer_id)
    if from_date:
        query = query.filter(Delivery.date >= from_date)
    if to_date:
        query = query.filter(Delivery.date <= to_date)
    return query.offset(skip).limit(limit).all()


@router.get("/customer/{customer_id}", response_model=List[DeliveryResponse])
def get_deliveries_by_customer(customer_id: int, db: Session = Depends(get_db)):
    return db.query(Delivery).filter(Delivery.customer_id == customer_id).all()


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(delivery_id: int, db: Session = Depends(get_db)):
    record = db.query(Delivery).filter(Delivery.delivery_id == delivery_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return record


@router.put("/{delivery_id}", response_model=DeliveryResponse)
def update_delivery(delivery_id: int, delivery: DeliveryUpdate, db: Session = Depends(get_db)):
    record = db.query(Delivery).filter(Delivery.delivery_id == delivery_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Delivery not found")
    for key, value in delivery.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{delivery_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_delivery(delivery_id: int, db: Session = Depends(get_db)):
    record = db.query(Delivery).filter(Delivery.delivery_id == delivery_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Delivery not found")
    db.delete(record)
    db.commit()
