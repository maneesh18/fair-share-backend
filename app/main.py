"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings
from app.db import engine
from sqlalchemy import text
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

# Run migrations on startup
@app.on_event("startup")
async def startup_event():
    """Run database migrations on startup."""
    try:
        logging.info("Running database migrations on startup...")
        
        # Check if tables exist
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'users'"))
            table_exists = result.scalar()
            
            if not table_exists:
                logging.info("Tables don't exist, running migrations...")
                import subprocess
                import sys
                
                # Run alembic upgrade head
                result = subprocess.run(
                    [sys.executable, "-m", "alembic", "upgrade", "head"],
                    capture_output=True,
                    text=True,
                    cwd="/opt/render/project/src"
                )
                
                if result.returncode == 0:
                    logging.info("Migrations completed successfully!")
                else:
                    logging.error(f"Migration failed: {result.stderr}")
                    raise Exception(f"Migration failed: {result.stderr}")
            else:
                logging.info("Tables already exist, skipping migrations")
                
    except Exception as e:
        logging.error(f"Startup migration error: {e}")
        raise

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
