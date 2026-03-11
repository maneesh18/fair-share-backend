"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.modules.auth.router import router as auth_router
from app.modules.groups.router import router as groups_router
from app.modules.expenses.router import router as expenses_router
from app.modules.receipts.router import router as receipts_router
from app.modules.disputes.router import router as disputes_router
from app.modules.ledger.router import router as ledger_router
from app.modules.trust_engine.router import router as trust_router
from app.modules.analytics.router import router as analytics_router

settings = get_settings()
app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(groups_router)
app.include_router(expenses_router)
app.include_router(receipts_router)
app.include_router(disputes_router)
app.include_router(ledger_router)
app.include_router(trust_router)
app.include_router(analytics_router)


@app.get("/health")
def health():
    return {"status": "ok"}
