from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import get_settings
from app.api import router as api_router
from sqlalchemy.engine.url import make_url
from app.db.base import Base
from app.db import models  # ensure models are imported for metadata
from app.db.session import engine
from app.ml.serve import model_service
from app.core.errors import http_exception_handler
import os
import sys
import logging
from pathlib import Path
from app.ml.model_loader import get_model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    # Create data directory for SQLite if needed, then create tables
    try:
        # Ensure data directory exists (for SQLite database)
        os.makedirs("./data", exist_ok=True)
        logger.info("Data directory created/verified")
        
        # Preload the model
        get_model()  
        
        db_url = get_settings().DATABASE_URL
        logger.info(f"Database URL: {db_url}")
        backend = make_url(db_url).get_backend_name()
        logger.info(f"Database backend: {backend}")
        
        if backend == "sqlite":
            logger.info("Setting up SQLite database...")
            Base.metadata.create_all(bind=engine)
            logger.info("SQLite tables created")
            
            # Try to initialize database with data
            try:
                logger.info("Attempting to import and call lancesqlite_Initialisation()...")
                from scripts.create_db import lancesqlite_Initialisation
                logger.info("Import successful, calling function...")
                lancesqlite_Initialisation()
                logger.info("Database initialized with employee data")
            except ImportError as e:
                logger.error(f"Failed to import lancesqlite_Initialisation: {e}")
            except Exception as e:
                logger.error(f"Database initialization failed: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
    
    try:
        model_service.load()
    except FileNotFoundError:
        logger.warning("Model file not found during startup; will load on first prediction.")
    
    yield
    try:
        model_service.close()
    except Exception:
        pass


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="0.1.0",
        lifespan=lifespan,
    )
    
    @app.get("/")
    async def root():
        """Root endpoint — redirects to API documentation."""
        return {
            "message": "Futurisys ML API",
            "version": "0.1.0",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

 
    return app



app = create_app()

#app.add_exception_handler(Exception, http_exception_handler)
