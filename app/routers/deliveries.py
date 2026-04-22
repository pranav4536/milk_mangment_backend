from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.delivery import Delivery, PaymentStatus
from app.schemas.delivery import DeliveryCreate, DeliveryUpdate, DeliveryResponse

router = APIRouter(prefix="/api/deliveries", tags=["Deliveries"])


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _derive_status(price: float, paid: float) -> PaymentStatus:
    if paid <= 0:
        return PaymentStatus.pending
    if paid >= price:
        return PaymentStatus.paid
    return PaymentStatus.partial


# ─── Create ───────────────────────────────────────────────────────────────────

@router.post("/", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(delivery: DeliveryCreate, db: Session = Depends(get_db)):
    price = delivery.price
    paid = delivery.paid_amount
    pending = round(price - paid, 4)

    db_delivery = Delivery(
        customer_id=delivery.customer_id,
        date=delivery.date,
        quantity=delivery.quantity,
        price=price,
        bottles_given=delivery.bottles_given,
        bottles_returned=delivery.bottles_returned,
        # ── transaction fields ──
        paid_amount=paid,
        pending_amount=pending,
        payment_mode=delivery.payment_mode,
        status=_derive_status(price, paid),
        notes=delivery.notes,
    )
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    return db_delivery


# ─── List with filters ────────────────────────────────────────────────────────

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
    return query.order_by(Delivery.date.desc()).offset(skip).limit(limit).all()


# ─── By customer shortcut ─────────────────────────────────────────────────────

@router.get("/customer/{customer_id}", response_model=List[DeliveryResponse])
def get_deliveries_by_customer(customer_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Delivery)
        .filter(Delivery.customer_id == customer_id)
        .order_by(Delivery.date.desc())
        .all()
    )


# ─── Single record ────────────────────────────────────────────────────────────

@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(delivery_id: int, db: Session = Depends(get_db)):
    record = db.query(Delivery).filter(Delivery.delivery_id == delivery_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return record


# ─── Update ───────────────────────────────────────────────────────────────────

@router.put("/{delivery_id}", response_model=DeliveryResponse)
def update_delivery(delivery_id: int, delivery: DeliveryUpdate, db: Session = Depends(get_db)):
    record = db.query(Delivery).filter(Delivery.delivery_id == delivery_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Delivery not found")

    data = delivery.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(record, key, value)

    # Re-derive pending_amount and status when price or paid_amount changes
    if "price" in data or "paid_amount" in data:
        price = record.price
        paid = record.paid_amount
        record.pending_amount = round(price - paid, 4)
        if "status" not in data:   # don't override an explicit status update
            record.status = _derive_status(price, paid)

    db.commit()
    db.refresh(record)
    return record


# ─── Delete ───────────────────────────────────────────────────────────────────

@router.delete("/{delivery_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_delivery(delivery_id: int, db: Session = Depends(get_db)):
    record = db.query(Delivery).filter(Delivery.delivery_id == delivery_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Delivery not found")
    db.delete(record)
    db.commit()
