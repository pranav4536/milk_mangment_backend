# 🥛 Milk Management Backend

A production-ready REST API for managing milk operations — built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL** (hosted on Render).

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
The `.env` file is already configured with the Render PostgreSQL connection.

### 3. Run the server
```bash
uvicorn app.main:app --reload
```

### 4. Open API docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📦 Project Structure

```
app/
├── main.py              # FastAPI entry point
├── database.py          # DB connection & session
├── models/              # SQLAlchemy ORM models
│   ├── vendor.py
│   ├── milk_collection.py
│   ├── customer.py
│   ├── delivery.py
│   └── bottle_tracking.py
├── schemas/             # Pydantic request/response models
│   ├── vendor.py
│   ├── milk_collection.py
│   ├── customer.py
│   ├── delivery.py
│   └── bottle_tracking.py
└── routers/             # API route handlers
    ├── vendors.py
    ├── milk_collection.py
    ├── customers.py
    ├── deliveries.py
    └── bottle_tracking.py
```

---

## 🗂️ API Endpoints

| Module | Base URL | Methods |
|---|---|---|
| Vendors | `/api/vendors` | GET, POST, PUT, DELETE |
| Milk Collection | `/api/milk-collection` | GET, POST, PUT, DELETE |
| Customers | `/api/customers` | GET, POST, PUT, DELETE |
| Deliveries | `/api/deliveries` | GET, POST, PUT, DELETE |
| Bottle Tracking | `/api/bottle-tracking` | GET, POST, PUT, DELETE |

### Special Endpoints
- `GET /api/milk-collection?vendor_id=1&from_date=2024-01-01&to_date=2024-01-31` — Filter by vendor and date
- `GET /api/milk-collection/vendor/{vendor_id}` — All collections for a vendor
- `GET /api/deliveries?customer_id=1&from_date=2024-01-01` — Filter deliveries
- `GET /api/deliveries/customer/{customer_id}` — All deliveries for a customer
- `GET /api/bottle-tracking/summary` — Overall pending bottle summary

---

## 🗄️ Database

| Table | Description |
|---|---|
| `vendors` | Milk vendors / suppliers |
| `milk_collection` | Daily milk collected from vendors |
| `customers` | Customer details with lat/long |
| `deliveries` | Daily deliveries to customers |
| `bottle_tracking` | Bottle given/returned/pending per customer |

---

## 🔧 Tech Stack

- **Framework**: FastAPI 0.111
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL (Render)
- **Validation**: Pydantic v2
- **Server**: Uvicorn
