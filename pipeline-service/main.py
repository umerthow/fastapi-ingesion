from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict
import uvicorn

from database import get_db, init_db
from models.customer import Customer
from services.ingestion import ingest_customers_with_dlt

# Initialize FastAPI app
app = FastAPI(
    title="FastAPI Pipeline Service",
    description="Data ingestion pipeline for customer data",
    version="1.0.0"
)

# Initialize database tables on startup
@app.on_event("startup")
def startup_event():
    """Initialize database tables on application startup."""
    print("Initializing database...")
    init_db()
    print("FastAPI Pipeline Service started successfully")

@app.get("/")
def root():
    """Root endpoint."""
    return {
        "service": "FastAPI Pipeline Service",
        "status": "running",
        "endpoints": {
            "ingest": "POST /api/ingest",
            "customers": "GET /api/customers",
            "customer_by_id": "GET /api/customers/{id}"
        }
    }

@app.post("/api/ingest")
def ingest_data(db: Session = Depends(get_db)) -> Dict:
    """
    Ingest customer data from Flask mock server into PostgreSQL.
    Fetches all data with auto-pagination and upserts into database.
    
    Returns:
        Dict with ingestion statistics
    """
    try:
        result = ingest_customers_with_dlt(db)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.get("/api/customers/{customer_id}")
def get_customer_by_id(customer_id: int, db: Session = Depends(get_db)) -> Dict:
    """
    Get a single customer by ID from database.
    
    Args:
        customer_id: The customer ID to fetch
    
    Returns:
        Customer data dictionary
    
    Raises:
        404: If customer not found
    """
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        
        if customer is None:
            raise HTTPException(
                status_code=404,
                detail=f"Customer with ID {customer_id} not found"
            )
        
        return customer.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch customer: {str(e)}")

@app.get("/api/customers")
def get_customers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get paginated list of customers from database.
    
    Args:
        page: Page number (default: 1)
        limit: Number of items per page (default: 10, max: 100)
    
    Returns:
        Dict with paginated customer data
    """
    try:
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get total count
        total_customers = db.query(Customer).count()
        
        # Get paginated customers
        customers = db.query(Customer).offset(offset).limit(limit).all()
        
        # Convert to dictionaries
        customer_list = [customer.to_dict() for customer in customers]
        
        # Calculate total pages
        total_pages = (total_customers + limit - 1) // limit
        
        return {
            "data": customer_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": total_customers,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch customers: {str(e)}")

@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "FastAPI Pipeline Service"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
