from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.get("/", response_model=List[CustomerResponse])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Customer).offset(skip).limit(limit).all()


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db)):
    db_customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, value in customer.model_dump(exclude_unset=True).items():
        setattr(db_customer, key, value)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(db_customer)
    db.commit()
