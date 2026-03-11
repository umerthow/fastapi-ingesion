# Multi-Service Data Pipeline

A data ingestion pipeline consisting of three Docker services: Flask mock server, FastAPI ingestion service, and PostgreSQL database.

## 🏗️ Architecture

**Data Flow:** Flask API (JSON) → FastAPI Pipeline (Ingest) → PostgreSQL → API Response

The system consists of:

1. **Flask Mock Server** - Provides customer data in JSON format via REST API
2. **FastAPI Pipeline** - Data ingestion service using `dlt` library
3. **PostgreSQL** - Primary data storage

---

## 🛠️ System Requirements

* Docker Desktop (running)
* Python 3.10+
* Git
* Docker Compose

---

## 📂 Project Structure

```text
project-root/
├── docker-compose.yml
├── .env
├── .env.example
├── README.md
├── mock-server/
│   ├── app.py
│   ├── data/customers.json
│   ├── Dockerfile
│   └── requirements.txt
└── pipeline-service/
    ├── main.py
    ├── models/customer.py
    ├── services/ingestion.py
    ├── database.py
    ├── Dockerfile
    └── requirements.txt
```

---

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/umerthow/fastapi-ingesiton.git
cd fastapi-ingesiton
```

### 2. Configure Environment Variables

Copy the example environment file and configure as needed:

```bash
cp .env.example .env
```

Default configuration in `.env`:
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=postgres`
- `POSTGRES_DB=customers_db`
- `FLASK_PORT=5000`
- `FASTAPI_PORT=8000`
- `POSTGRES_PORT=5432`

### 3. Start All Services

Build and start all services using Docker Compose:

```bash
docker-compose up -d --build
```

This will start:
- PostgreSQL database on port `5432`
- Flask mock server on port `5000`
- FastAPI pipeline service on port `8000`

### 4. Verify Services are Running

```bash
docker-compose ps
```

All three services should show as "Up" or "healthy".

---

## 📡 API Endpoints

### Flask Mock Server (Port 5000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check endpoint |
| GET | `/api/customers` | Get paginated list of customers |
| GET | `/api/customers/{id}` | Get single customer by ID |

**Query Parameters for `/api/customers`:**
- `page` (default: 1) - Page number
- `limit` (default: 10) - Items per page

### FastAPI Pipeline Service (Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check endpoint |
| POST | `/api/ingest` | Ingest data from Flask to PostgreSQL |
| GET | `/api/customers` | Get paginated list from database |
| GET | `/api/customers/{id}` | Get single customer by ID from database |

**Query Parameters for `/api/customers`:**
- `page` (default: 1) - Page number
- `limit` (default: 10, max: 100) - Items per page

---

## 🧪 Testing

### Automated Integration Tests

The project includes a comprehensive Python test suite using pytest.

#### Prerequisites

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

#### Run All Tests

```bash
# From project root
pytest tests/ -v

# Run specific test file
pytest tests/test_integration.py -v

# Run specific test class
pytest tests/test_integration.py::TestFlaskMockServer -v

# Run with detailed output on failures
pytest tests/ -v --tb=long
```

#### Test Coverage

The test suite includes **15 test cases** covering:

- ✅ **Service Availability** - Verify Flask and FastAPI services are running
- ✅ **Flask Mock Server** - Health check, pagination (2 pages), get by ID, 404 handling
- ✅ **Data Ingestion** - FastAPI ingests data from Flask successfully
- ✅ **FastAPI Pipeline** - Query customers from database, pagination, get by ID, 404 handling
- ✅ **Upsert Logic** - Verify no duplicate records on re-ingestion
- ✅ **Data Consistency** - Compare data between Flask and PostgreSQL

#### Expected Test Output

```
============================= test session starts ==============================
collected 15 items

tests/test_integration.py::TestServiceAvailability::test_flask_service_is_running PASSED
tests/test_integration.py::TestServiceAvailability::test_fastapi_service_is_running PASSED
tests/test_integration.py::TestFlaskMockServer::test_flask_health_endpoint PASSED
tests/test_integration.py::TestFlaskMockServer::test_flask_pagination_page_1 PASSED
tests/test_integration.py::TestFlaskMockServer::test_flask_pagination_page_2 PASSED
tests/test_integration.py::TestFlaskMockServer::test_flask_get_customer_by_id PASSED
tests/test_integration.py::TestFlaskMockServer::test_flask_customer_not_found PASSED
tests/test_integration.py::TestFastAPIIngestion::test_fastapi_health_endpoint PASSED
tests/test_integration.py::TestFastAPIIngestion::test_fastapi_data_ingestion PASSED
tests/test_integration.py::TestFastAPIPipeline::test_fastapi_get_customers_from_database PASSED
tests/test_integration.py::TestFastAPIPipeline::test_fastapi_get_customer_by_id PASSED
tests/test_integration.py::TestFastAPIPipeline::test_fastapi_customer_not_found PASSED
tests/test_integration.py::TestUpsertLogic::test_upsert_no_duplicates_on_reingestion PASSED
tests/test_integration.py::TestFastAPIPagination::test_fastapi_pagination_multiple_pages PASSED
tests/test_integration.py::TestDataConsistency::test_data_consistency_flask_vs_database PASSED

============================== 15 passed in 0.86s ==============================
```

---

## 🔧 Manual Testing with cURL

### 1. Test Flask Mock Server

Check health:
```bash
curl http://localhost:5000/api/health
```

Get paginated customers:
```bash
curl http://localhost:5000/api/customers?page=1&limit=5
```

Get single customer:
```bash
curl http://localhost:5000/api/customers/1
```

### 2. Test Data Ingestion

Ingest data from Flask to PostgreSQL:
```bash
curl -X POST http://localhost:8000/api/ingest
```

Expected response:
```json
{
  "status": "success",
  "records_fetched": 25,
  "records_processed": 25,
  "message": "Successfully ingested 25 customers"
}
```

### 3. Test FastAPI Pipeline

Get customers from database:
```bash
curl http://localhost:8000/api/customers?page=1&limit=5
```

Get single customer from database:
```bash
curl http://localhost:8000/api/customers/1
```

### 4. Test Re-ingestion (Upsert Logic)

Run ingestion again to verify upsert works (no duplicates):
```bash
curl -X POST http://localhost:8000/api/ingest
```

---

## 💾 Database Schema

The `customers` table in PostgreSQL has the following structure:

| Column | Type | Constraints |
|--------|------|-------------|
| customer_id | INTEGER | PRIMARY KEY |
| first_name | VARCHAR(100) | NOT NULL |
| last_name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(255) | NOT NULL |
| phone | VARCHAR(20) | - |
| address | VARCHAR(500) | - |
| date_of_birth | VARCHAR(50) | - |
| account_balance | NUMERIC(15, 2) | - |
| created_at | VARCHAR(50) | - |

---

## 🔧 Useful Commands

### View Service Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f mock-server
docker-compose logs -f pipeline-service
docker-compose logs -f postgres
```

### Restart a Service

```bash
docker-compose restart <service-name>
```

### Rebuild a Service

```bash
docker-compose up -d --build <service-name>
```

### Stop All Services

```bash
docker-compose down
```

### Stop and Remove Volumes (Reset Database)

```bash
docker-compose down -v
```

### Access PostgreSQL Database

```bash
docker exec -it postgres_db psql -U postgres -d customers_db
```

Useful SQL commands:
```sql
-- View all customers
SELECT * FROM customers;

-- Count customers
SELECT COUNT(*) FROM customers;

-- View table schema
\d customers

-- Exit
\q
```

---

## 🔍 Features

- ✅ **Auto-pagination** - FastAPI automatically fetches all pages from Flask
- ✅ **Upsert logic** - Updates existing records or inserts new ones (no duplicates)
- ✅ **Data validation** - SQLAlchemy models with proper constraints
- ✅ **Error handling** - Comprehensive error handling and logging
- ✅ **Health checks** - Docker health checks for all services
- ✅ **Environment configuration** - Configurable via `.env` file
- ✅ **RESTful APIs** - Standard REST endpoints with proper status codes

---

## 📝 Data Source

The Flask mock server serves 25 sample customers from `mock-server/data/customers.json` with realistic data including:
- Names and contact information
- Addresses across various US cities
- Account balances
- Date of birth
- Creation timestamps

---

## 📄 License

This project is created for educational and assessment purposes.
