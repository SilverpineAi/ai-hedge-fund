import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.backend.routes import api_router
from app.backend.database import create_tables
from app.backend.utils.logging import setup_logging, get_logger

# Setup logging
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_to_file=os.getenv("LOG_TO_FILE", "true").lower() == "true"
)

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Sales Intelligence Platform API...")
    
    # Create database tables on startup
    try:
        await create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    logger.info("API startup complete")
    yield
    
    logger.info("Shutting down Sales Intelligence Platform API...")

app = FastAPI(
    title="Sales Intelligence Platform API", 
    description="Backend API for Sales Intelligence Platform - Lead processing, enrichment, and prioritization", 
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(api_router)
