"""
Integration Test Suite for Multi-Service Data Pipeline
Tests: Docker services, Flask API, FastAPI ingestion, and all endpoints

Requirements:
    pip install pytest requests

Usage:
    pytest test_integration.py -v
"""

import pytest
import requests
import time
from typing import Dict, Any


# Configuration
FLASK_BASE_URL = "http://localhost:5000"
FASTAPI_BASE_URL = "http://localhost:8000"


class TestServiceAvailability:
    """Test 1: Verify all services are running and accessible"""
    
    def test_flask_service_is_running(self):
        """Flask mock server should be accessible"""
        response = requests.get(f"{FLASK_BASE_URL}/api/health")
        assert response.status_code == 200, "Flask service is not running"
        
    def test_fastapi_service_is_running(self):
        """FastAPI pipeline service should be accessible"""
        response = requests.get(f"{FASTAPI_BASE_URL}/api/health")
        assert response.status_code == 200, "FastAPI service is not running"


class TestFlaskMockServer:
    """Test 2-6: Flask serves data with pagination and handles requests correctly"""
    
    def test_flask_health_endpoint(self):
        """Flask health check should return 200"""
        response = requests.get(f"{FLASK_BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "customers_loaded" in data
        
    def test_flask_pagination_page_1(self):
        """Flask should return paginated data for page 1"""
        response = requests.get(f"{FLASK_BASE_URL}/api/customers", params={"page": 1, "limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert len(data["data"]) == 5
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 5
        
    def test_flask_pagination_page_2(self):
        """Flask should return paginated data for page 2"""
        response = requests.get(f"{FLASK_BASE_URL}/api/customers", params={"page": 2, "limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 5
        assert data["pagination"]["page"] == 2
        
    def test_flask_get_customer_by_id(self):
        """Flask should return a single customer by ID"""
        response = requests.get(f"{FLASK_BASE_URL}/api/customers/1")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == 1
        assert "first_name" in data
        assert "last_name" in data
        assert "email" in data
        
    def test_flask_customer_not_found(self):
        """Flask should return 404 for non-existent customer"""
        response = requests.get(f"{FLASK_BASE_URL}/api/customers/9999")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data


class TestFastAPIIngestion:
    """Test 7-8: FastAPI ingests data successfully from Flask"""
    
    def test_fastapi_health_endpoint(self):
        """FastAPI health check should return 200"""
        response = requests.get(f"{FASTAPI_BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        
    def test_fastapi_data_ingestion(self):
        """FastAPI should successfully ingest data from Flask"""
        response = requests.post(f"{FASTAPI_BASE_URL}/api/ingest")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "records_fetched" in data
        assert "records_processed" in data
        assert data["records_processed"] > 0
        assert data["records_fetched"] == data["records_processed"]
        print(f"\n   ✓ Ingested {data['records_processed']} records successfully")


class TestFastAPIPipeline:
    """Test 9-11: FastAPI returns data from database correctly"""
    
    def test_fastapi_get_customers_from_database(self):
        """FastAPI should return customers from PostgreSQL"""
        response = requests.get(f"{FASTAPI_BASE_URL}/api/customers", params={"page": 1, "limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert len(data["data"]) > 0
        assert data["pagination"]["page"] == 1
        
    def test_fastapi_get_customer_by_id(self):
        """FastAPI should return a single customer by ID from database"""
        response = requests.get(f"{FASTAPI_BASE_URL}/api/customers/1")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == 1
        assert "first_name" in data
        assert "email" in data
        
    def test_fastapi_customer_not_found(self):
        """FastAPI should return 404 for non-existent customer"""
        response = requests.get(f"{FASTAPI_BASE_URL}/api/customers/9999")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestUpsertLogic:
    """Test 12: Verify upsert logic prevents duplicates on re-ingestion"""
    
    def test_upsert_no_duplicates_on_reingestion(self):
        """Re-ingestion should not create duplicate records"""
        # Get initial count
        response1 = requests.get(f"{FASTAPI_BASE_URL}/api/customers", params={"page": 1, "limit": 100})
        assert response1.status_code == 200
        initial_count = response1.json()["pagination"]["total_items"]
        
        # Re-ingest data
        ingest_response = requests.post(f"{FASTAPI_BASE_URL}/api/ingest")
        assert ingest_response.status_code == 200
        assert ingest_response.json()["status"] == "success"
        
        # Get count after re-ingestion
        response2 = requests.get(f"{FASTAPI_BASE_URL}/api/customers", params={"page": 1, "limit": 100})
        assert response2.status_code == 200
        final_count = response2.json()["pagination"]["total_items"]
        
        # Count should remain the same
        assert initial_count == final_count, f"Duplicates detected! Initial: {initial_count}, Final: {final_count}"
        print(f"\n   ✓ No duplicates created. Total customers: {final_count}")


class TestFastAPIPagination:
    """Test 13: Verify FastAPI pagination works correctly"""
    
    def test_fastapi_pagination_multiple_pages(self):
        """FastAPI should handle pagination correctly"""
        # Get page 1
        response1 = requests.get(f"{FASTAPI_BASE_URL}/api/customers", params={"page": 1, "limit": 5})
        assert response1.status_code == 200
        page1_data = response1.json()
        
        # Get page 2
        response2 = requests.get(f"{FASTAPI_BASE_URL}/api/customers", params={"page": 2, "limit": 5})
        assert response2.status_code == 200
        page2_data = response2.json()
        
        # Verify pagination metadata
        assert page1_data["pagination"]["page"] == 1
        assert page2_data["pagination"]["page"] == 2
        assert page1_data["pagination"]["total_items"] == page2_data["pagination"]["total_items"]
        
        # Verify different data on different pages
        page1_ids = [c["customer_id"] for c in page1_data["data"]]
        page2_ids = [c["customer_id"] for c in page2_data["data"]]
        assert len(set(page1_ids) & set(page2_ids)) == 0, "Pages should contain different customers"
        print(f"\n   ✓ Pagination working correctly. Total items: {page1_data['pagination']['total_items']}")


class TestDataConsistency:
    """Additional test: Verify data consistency between Flask and PostgreSQL"""
    
    def test_data_consistency_flask_vs_database(self):
        """Data in PostgreSQL should match data from Flask"""
        # Get customer 1 from Flask
        flask_response = requests.get(f"{FLASK_BASE_URL}/api/customers/1")
        flask_data = flask_response.json()
        
        # Get customer 1 from FastAPI (PostgreSQL)
        fastapi_response = requests.get(f"{FASTAPI_BASE_URL}/api/customers/1")
        fastapi_data = fastapi_response.json()
        
        # Compare key fields
        assert flask_data["customer_id"] == fastapi_data["customer_id"]
        assert flask_data["first_name"] == fastapi_data["first_name"]
        assert flask_data["last_name"] == fastapi_data["last_name"]
        assert flask_data["email"] == fastapi_data["email"]
        print(f"\n   ✓ Data consistency verified for customer {flask_data['customer_id']}")


if __name__ == "__main__":
    """Run tests with pytest when executed directly"""
    import sys
    pytest.main([__file__, "-v", "--tb=short"] + sys.argv[1:])
