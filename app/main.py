from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, query, anomalies
from app.config import settings
from app.data.database import init_db
from app.utils.logging_config import logger
import uvicorn

app = FastAPI(
    title=settings.APP_NAME,
    description="API for AI Support Ticket Analytics",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(query.router, tags=["Query"])
app.include_router(anomalies.router, tags=["Anomalies"])

@app.on_event("startup")
def startup_event():
    logger.info("Starting up application, initializing database...")
    init_db()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
