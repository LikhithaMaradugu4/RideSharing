from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.api.routers import auth
from app.api.routers import test_protected
from app.api.v1 import drivers,tenant_admin,riders,ride_requests,pricing,driver_trips
from app.api.v1 import payments


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

# 👇 AFTER app is created
app.include_router(auth.router)
app.include_router(test_protected.router)
app.include_router(drivers.router)
app.include_router(tenant_admin.router)
app.include_router(riders.router)
app.include_router(ride_requests.router)
app.include_router(pricing.router)
app.include_router(driver_trips.router)
app.include_router(payments.router)


@app.get("/")
def root():
    return {"status": "Backend running"}
