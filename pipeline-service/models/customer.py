from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from database import Base

class Customer(Base):
    """
    Customer model for storing customer information.
    Matches the structure from Flask mock server.
    """
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    date_of_birth = Column(String(50), nullable=True)
    account_balance = Column(Numeric(15, 2), nullable=True)
    created_at = Column(String(50), nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Customer(id={self.customer_id}, name={self.first_name} {self.last_name}, email={self.email})>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "customer_id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "date_of_birth": self.date_of_birth,
            "account_balance": float(self.account_balance) if self.account_balance else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
