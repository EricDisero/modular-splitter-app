"""
Main FastAPI application for the Splitter service.
This service handles audio processing with HTDemucs model.
"""
import os
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.routes import split
from app.utils.audio import setup_processing_dirs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(name)s | %(message)s'
)
logger = logging.getLogger("splitter-service")

# Initialize FastAPI app
app = FastAPI(
    title="Splitter Service API",
    description="GPU-powered audio stem separation service using HTDemucs",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restricted in production via Fly.io
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(split.router)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Execute actions on application startup."""
    logger.info("Starting Splitter Service")

    # Set up processing directories
    setup_processing_dirs()

    # Log GPU availability for debugging
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        gpu_count = torch.cuda.device_count() if gpu_available else 0
        gpu_name = torch.cuda.get_device_name(0) if gpu_available and gpu_count > 0 else "None"

        logger.info(f"GPU Available: {gpu_available}")
        logger.info(f"GPU Count: {gpu_count}")
        logger.info(f"GPU Name: {gpu_name}")
    except ImportError:
        logger.warning("PyTorch not installed, GPU status unknown")
    except Exception as e:
        logger.error(f"Error checking GPU status: {str(e)}")


# Health check endpoint
@app.get("/ping")
async def ping():
    """
    Health check endpoint that returns a simple status.
    """
    return {"status": "ok", "service": "splitter-service"}