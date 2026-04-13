from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.transaction import VendorTransaction, PaymentStatus
from app.schemas.transaction import (
    VendorTransactionCreate,
    VendorTransactionUpdate,
    VendorTransactionResponse,
)

router = APIRouter(prefix="/api/vendor-transactions", tags=["Vendor Transactions"])


def _derive_status(total: float, paid: float) -> PaymentStatus:
    if paid <= 0:
        return PaymentStatus.pending
    if paid >= total:
        return PaymentStatus.paid
    return PaymentStatus.partial


# ─── Create ───────────────────────────────────────────────────────────────────

@router.post("/", response_model=VendorTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_vendor_transaction(payload: VendorTransactionCreate, db: Session = Depends(get_db)):
    total = round(payload.milk_qty * payload.rate, 4)
    paid = payload.paid_amount
    due = round(total - paid, 4)
    txn = VendorTransaction(
        vendor_id=payload.vendor_id,
        date=payload.date,
        milk_qty=payload.milk_qty,
        rate=payload.rate,
        total_amount=total,
        paid_amount=paid,
        due_amount=due,
        status=_derive_status(total, paid),
        notes=payload.notes,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


# ─── List with filters ────────────────────────────────────────────────────────

@router.get("/", response_model=List[VendorTransactionResponse])
def list_vendor_transactions(
    vendor_id: Optional[int] = Query(None),
    status: Optional[PaymentStatus] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(VendorTransaction)
    if vendor_id is not None:
        q = q.filter(VendorTransaction.vendor_id == vendor_id)
    if status:
        q = q.filter(VendorTransaction.status == status)
    if from_date:
        q = q.filter(VendorTransaction.date >= from_date)
    if to_date:
        q = q.filter(VendorTransaction.date <= to_date)
    return q.order_by(VendorTransaction.date.desc()).offset(skip).limit(limit).all()


# ─── By vendor shortcut ───────────────────────────────────────────────────────

@router.get("/vendor/{vendor_id}", response_model=List[VendorTransactionResponse])
def get_by_vendor(
    vendor_id: int,
    status: Optional[PaymentStatus] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(VendorTransaction).filter(VendorTransaction.vendor_id == vendor_id)
    if status:
        q = q.filter(VendorTransaction.status == status)
    if from_date:
        q = q.filter(VendorTransaction.date >= from_date)
    if to_date:
        q = q.filter(VendorTransaction.date <= to_date)
    return q.order_by(VendorTransaction.date.desc()).all()


# ─── Single record ────────────────────────────────────────────────────────────

@router.get("/{transaction_id}", response_model=VendorTransactionResponse)
def get_vendor_transaction(transaction_id: int, db: Session = Depends(get_db)):
    record = db.query(VendorTransaction).filter(
        VendorTransaction.transaction_id == transaction_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Vendor transaction not found")
    return record


# ─── Update ───────────────────────────────────────────────────────────────────

@router.put("/{transaction_id}", response_model=VendorTransactionResponse)
def update_vendor_transaction(
    transaction_id: int, payload: VendorTransactionUpdate, db: Session = Depends(get_db)
):
    record = db.query(VendorTransaction).filter(
        VendorTransaction.transaction_id == transaction_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Vendor transaction not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(record, key, value)

    # Recompute derived fields
    total = round(record.milk_qty * record.rate, 4)
    record.total_amount = total
    record.due_amount = round(total - record.paid_amount, 4)
    if "status" not in data:
        record.status = _derive_status(total, record.paid_amount)

    db.commit()
    db.refresh(record)
    return record


# ─── Delete ───────────────────────────────────────────────────────────────────

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vendor_transaction(transaction_id: int, db: Session = Depends(get_db)):
    record = db.query(VendorTransaction).filter(
        VendorTransaction.transaction_id == transaction_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Vendor transaction not found")
    db.delete(record)
    db.commit()
