import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.core.database import engine
from app.api.routes import auth, categories, complaints, notices, notifications, dashboard

app = FastAPI(title="Society Maintenance Tracker", version="0.1.0")

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(complaints.router, prefix="/api")
app.include_router(notices.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

# Mount local uploads directory for files uploaded locally
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health")
def health_check():
    """Basic health check — verifies the API is running."""
    return {"status": "ok"}


@app.get("/health/db")
def db_health_check():
    """Verify database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        return {"status": "error", "database": str(exc)}