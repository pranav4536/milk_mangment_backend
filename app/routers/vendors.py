from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorResponse

router = APIRouter(prefix="/api/vendors", tags=["Vendors"])


@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    db_vendor = Vendor(**vendor.model_dump())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor


@router.get("/", response_model=List[VendorResponse])
def list_vendors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Vendor).offset(skip).limit(limit).all()


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    db_vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return db_vendor


@router.put("/{vendor_id}", response_model=VendorResponse)
def update_vendor(vendor_id: int, vendor: VendorUpdate, db: Session = Depends(get_db)):
    db_vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    for key, value in vendor.model_dump(exclude_unset=True).items():
        setattr(db_vendor, key, value)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    db_vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    db.delete(db_vendor)
    db.commit()
