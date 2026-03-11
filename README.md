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
git clone <repository-url>
cd fastapi-ingesion
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
- `FLASK_PORT=5001`
- `FASTAPI_PORT=8000`
- `POSTGRES_PORT=5432`

### 3. Start All Services

Build and start all services using Docker Compose:

```bash
docker-compose up -d --build
```

This will start:
- PostgreSQL database on port `5432`
- Flask mock server on port `5001`
- FastAPI pipeline service on port `8000`

### 4. Verify Services are Running

```bash
docker-compose ps
```

All three services should show as "Up" or "healthy".

---

## 📡 API Endpoints

### Flask Mock Server (Port 5001)

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

## 🧪 Testing the Service

### 1. Test Flask Mock Server

Check health:
```bash
curl http://localhost:5001/api/health
```

Get paginated customers:
```bash
curl http://localhost:5001/api/customers?page=1&limit=5
```

Get single customer:
```bash
curl http://localhost:5001/api/customers/1
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

## 🛑 Troubleshooting

### Port 5000 Already in Use (macOS)

If port 5000 is occupied by AirPlay on macOS, the service is configured to use port 5001 instead. Update the `.env` file if needed.

### Services Not Starting

Check Docker Desktop is running:
```bash
docker ps
```

View service logs for errors:
```bash
docker-compose logs
```

### Database Connection Issues

Ensure PostgreSQL is healthy:
```bash
docker-compose ps postgres
```

Restart the database:
```bash
docker-compose restart postgres
```

### Ingestion Returns 0 Records

1. Check if Flask mock server is accessible from pipeline service
2. View pipeline service logs: `docker-compose logs pipeline-service`
3. Ensure the database table exists and has correct schema

---

## 📄 License

This project is created for educational and assessment purposes.
