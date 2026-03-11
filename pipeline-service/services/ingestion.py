import requests
from typing import List, Dict
import dlt
from sqlalchemy.orm import Session
from models.customer import Customer
import os

# Get mock server URL from environment variable
MOCK_SERVER_URL = os.getenv("MOCK_SERVER_URL", "http://localhost:5001")

def fetch_all_customers_from_flask() -> List[Dict]:
    """
    Fetch all customers from Flask mock server with auto-pagination.
    Returns a list of all customer records.
    """
    all_customers = []
    page = 1
    limit = 10
    
    print(f"Starting to fetch customers from {MOCK_SERVER_URL}")
    
    while True:
        try:
            # Fetch paginated data
            url = f"{MOCK_SERVER_URL}/api/customers"
            params = {"page": page, "limit": limit}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            customers = data.get("data", [])
            pagination = data.get("pagination", {})
            
            if not customers:
                break
            
            all_customers.extend(customers)
            print(f"Fetched page {page}: {len(customers)} customers")
            
            # Check if there are more pages
            if not pagination.get("has_next", False):
                break
            
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching customers from Flask: {e}")
            raise Exception(f"Failed to fetch data from mock server: {e}")
    
    print(f"Total customers fetched: {len(all_customers)}")
    return all_customers

def upsert_customers(db: Session, customers: List[Dict]) -> int:
    """
    Upsert customers into the database.
    Updates existing records or inserts new ones.
    Returns the number of records processed.
    """
    records_processed = 0
    
    for customer_data in customers:
        try:
            # Check if customer exists
            existing_customer = db.query(Customer).filter(
                Customer.customer_id == customer_data["customer_id"]
            ).first()
            
            if existing_customer:
                # Update existing customer
                for key, value in customer_data.items():
                    if key != "customer_id":
                        setattr(existing_customer, key, value)
                print(f"Updated customer ID: {customer_data['customer_id']}")
            else:
                # Insert new customer
                new_customer = Customer(**customer_data)
                db.add(new_customer)
                print(f"Inserted new customer ID: {customer_data['customer_id']}")
            
            records_processed += 1
            
        except Exception as e:
            print(f"Error processing customer {customer_data.get('customer_id')}: {e}")
            continue
    
    # Commit all changes
    db.commit()
    print(f"Successfully processed {records_processed} customers")
    
    return records_processed

@dlt.source
def customers_source():
    """
    DLT source function to fetch customer data.
    Uses dlt library for data ingestion.
    """
    customers = fetch_all_customers_from_flask()
    return dlt.resource(customers, name="customers")

def ingest_customers_with_dlt(db: Session) -> Dict:
    """
    Main ingestion function using dlt library.
    Fetches data from Flask and upserts into PostgreSQL.
    Returns statistics about the ingestion process.
    """
    try:
        print("Starting customer data ingestion with dlt...")
        
        # Fetch all customers using dlt source
        source = customers_source()
        customers = list(source.customers)
        
        # Upsert customers into database
        records_processed = upsert_customers(db, customers)
        
        return {
            "status": "success",
            "records_fetched": len(customers),
            "records_processed": records_processed,
            "message": f"Successfully ingested {records_processed} customers"
        }
        
    except Exception as e:
        print(f"Error during ingestion: {e}")
        return {
            "status": "error",
            "records_fetched": 0,
            "records_processed": 0,
            "message": f"Ingestion failed: {str(e)}"
        }
