from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.milk_collection import MilkCollection
from app.schemas.milk_collection import MilkCollectionCreate, MilkCollectionUpdate, MilkCollectionResponse

router = APIRouter(prefix="/api/milk-collection", tags=["Milk Collection"])


@router.post("/", response_model=MilkCollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(collection: MilkCollectionCreate, db: Session = Depends(get_db)):
    db_collection = MilkCollection(**collection.model_dump())
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return db_collection


@router.get("/", response_model=List[MilkCollectionResponse])
def list_collections(
    vendor_id: Optional[int] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(MilkCollection)
    if vendor_id:
        query = query.filter(MilkCollection.vendor_id == vendor_id)
    if from_date:
        query = query.filter(MilkCollection.date >= from_date)
    if to_date:
        query = query.filter(MilkCollection.date <= to_date)
    return query.offset(skip).limit(limit).all()


@router.get("/vendor/{vendor_id}", response_model=List[MilkCollectionResponse])
def get_collections_by_vendor(vendor_id: int, db: Session = Depends(get_db)):
    return db.query(MilkCollection).filter(MilkCollection.vendor_id == vendor_id).all()


@router.get("/{id}", response_model=MilkCollectionResponse)
def get_collection(id: int, db: Session = Depends(get_db)):
    record = db.query(MilkCollection).filter(MilkCollection.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Collection record not found")
    return record


@router.put("/{id}", response_model=MilkCollectionResponse)
def update_collection(id: int, collection: MilkCollectionUpdate, db: Session = Depends(get_db)):
    record = db.query(MilkCollection).filter(MilkCollection.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Collection record not found")
    for key, value in collection.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(id: int, db: Session = Depends(get_db)):
    record = db.query(MilkCollection).filter(MilkCollection.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Collection record not found")
    db.delete(record)
    db.commit()
