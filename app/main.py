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
import subprocess
from pathlib import Path
from app.ml.model_loader import get_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    # Create data directory for SQLite if needed, then create tables
    try:
        # Ensure data directory exists (for SQLite database)
        os.makedirs("./data", exist_ok=True)
        
        # Preload the model
        get_model()  
        
        if make_url(get_settings().DATABASE_URL).get_backend_name() == "sqlite":
            Base.metadata.create_all(bind=engine)
            try:
                script_path = Path(__file__).resolve().parents[1] / "scripts" / "create_db.py"
                subprocess.run([sys.executable, str(script_path)], check=True)
            except Exception:
                pass
    except Exception as e:
        import logging
        logging.warning(f"Startup error: {e}")
    
    try:
        model_service.load()
    except FileNotFoundError:
        import logging
        logging.warning("Model file not found during startup; will load on first prediction.")
    
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
