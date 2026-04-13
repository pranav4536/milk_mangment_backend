from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base

# Import all models so SQLAlchemy registers them before creating tables
from app.models import vendor, milk_collection, customer, delivery, bottle_tracking  # noqa: F401
from app.models import transaction, customer_plan  # noqa: F401

from app.routers import vendors, milk_collection as mc_router, customers, deliveries, bottle_tracking as bt_router
from app.routers import transactions as cust_txn_router, vendor_transactions as vend_txn_router, plans as plans_router

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Milk Management API",
    description=(
        "A complete REST API for managing milk operations: "
        "vendor collection, customer deliveries, and bottle tracking."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow all origins for development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(vendors.router)
app.include_router(mc_router.router)
app.include_router(customers.router)
app.include_router(deliveries.router)
app.include_router(bt_router.router)
app.include_router(cust_txn_router.router)
app.include_router(vend_txn_router.router)
app.include_router(plans_router.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "🥛 Milk Management API is running!",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
