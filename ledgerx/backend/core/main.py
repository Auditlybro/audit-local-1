"""
LedgerX — FastAPI core application.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.redis import close_redis
from routers import health, auth, companies, ledgers, stock, vouchers, reports, gst, banking, imports, exports, activity


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown."""
    yield
    await close_redis()


app = FastAPI(
    title="LedgerX API",
    description="Accounting platform for Indian CAs and SMEs",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health")
app.include_router(auth.router, prefix="/auth")
app.include_router(companies.router, prefix="/companies")
app.include_router(ledgers.router, prefix="/companies")
app.include_router(stock.router, prefix="/companies")
app.include_router(vouchers.router, prefix="/companies")
app.include_router(reports.router, prefix="/companies")
app.include_router(gst.router, prefix="/companies")
app.include_router(banking.router, prefix="/companies")
app.include_router(imports.router, prefix="/companies")
app.include_router(exports.router, prefix="/companies")
app.include_router(activity.router)


@app.get("/")
async def root():
    return {"app": "LedgerX", "status": "ok"}
