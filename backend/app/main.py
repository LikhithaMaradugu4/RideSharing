from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.database import engine, Base
from app.api.routers import auth
from app.api.routers import test_protected
from app.api.v1 import drivers,tenant_admin,riders,ride_requests,pricing,driver_trips,trips
from app.api.v1 import payments
from app.api import v2, admin
from fastapi.middleware.cors import CORSMiddleware



@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

# Add CORS middleware FIRST, before any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],  # React app and Vite ports
    allow_credentials=True,
    allow_methods=["*"],  # allows POST, GET, OPTIONS, etc.
    allow_headers=["*"],  # allows X-Session-ID
)

""" # 👇 AFTER app is created
# Phase-1 routes (session-based auth)
app.include_router(auth.router)
app.include_router(test_protected.router)
app.include_router(drivers.router)
app.include_router(tenant_admin.router)
app.include_router(riders.router)
app.include_router(ride_requests.router)
app.include_router(pricing.router)
app.include_router(driver_trips.router)
app.include_router(trips.router)
app.include_router(payments.router) """

# Phase-1 routes (session-based auth)
app.include_router(auth.router)

# Phase-2 routes (JWT-based auth)
app.include_router(v2.router, prefix="/api/v2")

# Admin routes (session-based auth)
app.include_router(admin.router, prefix="/api/admin")

# Static files for uploaded documents (secured by JWT in production)
upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")


@app.get("/")
def root():
    return {"status": "Backend running"}
