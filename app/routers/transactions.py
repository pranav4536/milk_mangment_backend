from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.transaction import CustomerTransaction, CustomerPaymentMode, PaymentStatus
from app.schemas.transaction import (
    CustomerTransactionCreate,
    CustomerTransactionUpdate,
    CustomerTransactionResponse,
)

router = APIRouter(prefix="/api/customer-transactions", tags=["Customer Transactions"])


def _derive_status(total: float, paid: float) -> PaymentStatus:
    if paid <= 0:
        return PaymentStatus.pending
    if paid >= total:
        return PaymentStatus.paid
    return PaymentStatus.partial


# ─── Create ───────────────────────────────────────────────────────────────────

@router.post("/", response_model=CustomerTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_customer_transaction(payload: CustomerTransactionCreate, db: Session = Depends(get_db)):
    total = payload.total_amount
    paid = payload.paid_amount
    pending = round(total - paid, 4)
    txn = CustomerTransaction(
        customer_id=payload.customer_id,
        date=payload.date,
        total_amount=total,
        paid_amount=paid,
        pending_amount=pending,
        payment_mode=payload.payment_mode,
        status=_derive_status(total, paid),
        notes=payload.notes,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


# ─── List with filters ────────────────────────────────────────────────────────

@router.get("/", response_model=List[CustomerTransactionResponse])
def list_customer_transactions(
    customer_id: Optional[int] = Query(None),
    payment_mode: Optional[CustomerPaymentMode] = Query(None),
    status: Optional[PaymentStatus] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(CustomerTransaction)
    if customer_id is not None:
        q = q.filter(CustomerTransaction.customer_id == customer_id)
    if payment_mode:
        q = q.filter(CustomerTransaction.payment_mode == payment_mode)
    if status:
        q = q.filter(CustomerTransaction.status == status)
    if from_date:
        q = q.filter(CustomerTransaction.date >= from_date)
    if to_date:
        q = q.filter(CustomerTransaction.date <= to_date)
    return q.order_by(CustomerTransaction.date.desc()).offset(skip).limit(limit).all()


# ─── By customer shortcut ─────────────────────────────────────────────────────

@router.get("/customer/{customer_id}", response_model=List[CustomerTransactionResponse])
def get_by_customer(
    customer_id: int,
    status: Optional[PaymentStatus] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(CustomerTransaction).filter(CustomerTransaction.customer_id == customer_id)
    if status:
        q = q.filter(CustomerTransaction.status == status)
    if from_date:
        q = q.filter(CustomerTransaction.date >= from_date)
    if to_date:
        q = q.filter(CustomerTransaction.date <= to_date)
    return q.order_by(CustomerTransaction.date.desc()).all()


# ─── Single record ────────────────────────────────────────────────────────────

@router.get("/{transaction_id}", response_model=CustomerTransactionResponse)
def get_customer_transaction(transaction_id: int, db: Session = Depends(get_db)):
    record = db.query(CustomerTransaction).filter(
        CustomerTransaction.transaction_id == transaction_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Customer transaction not found")
    return record


# ─── Update ───────────────────────────────────────────────────────────────────

@router.put("/{transaction_id}", response_model=CustomerTransactionResponse)
def update_customer_transaction(
    transaction_id: int, payload: CustomerTransactionUpdate, db: Session = Depends(get_db)
):
    record = db.query(CustomerTransaction).filter(
        CustomerTransaction.transaction_id == transaction_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Customer transaction not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(record, key, value)

    # Recompute derived fields if totals changed
    total = record.total_amount
    paid = record.paid_amount
    record.pending_amount = round(total - paid, 4)
    if "status" not in data:  # don't override explicit status update
        record.status = _derive_status(total, paid)

    db.commit()
    db.refresh(record)
    return record


# ─── Delete ───────────────────────────────────────────────────────────────────

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer_transaction(transaction_id: int, db: Session = Depends(get_db)):
    record = db.query(CustomerTransaction).filter(
        CustomerTransaction.transaction_id == transaction_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Customer transaction not found")
    db.delete(record)
    db.commit()
