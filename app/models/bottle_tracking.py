from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class BottleTracking(Base):
    __tablename__ = "bottle_tracking"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, unique=True)
    total_given = Column(Integer, default=0)
    total_returned = Column(Integer, default=0)
    pending = Column(Integer, default=0)   # computed: total_given - total_returned

    customer = relationship("Customer", backref="bottle_tracking")
