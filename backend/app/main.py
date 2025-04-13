"""
Main FastAPI application for the Splitter App backend.
This module handles routing, middleware, and application setup.
"""
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes import ping, keygen, upload, split
from app.utils.sessions import validate_session
from app.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Splitter App Backend API",
    description="Backend API for audio stem separation application",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(ping.router)
app.include_router(keygen.router)
app.include_router(upload.router)
app.include_router(split.router)


# Session validation middleware
@app.middleware("http")
async def session_validation_middleware(request: Request, call_next):
    """
    Middleware to validate session before processing the request.
    Public routes like ping and license validation are exempt.
    """
    # Paths that don't require license validation
    exempt_paths = [
        "/ping",
        "/api/validate-license",
        "/docs",
        "/redoc",
        "/openapi.json"
    ]

    # Check if path is exempt
    if any(request.url.path.startswith(path) for path in exempt_paths):
        return await call_next(request)

    # Validate session
    valid = await validate_session(request)
    if not valid:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid or expired license. Please validate your license."}
        )

    # Continue processing if session is valid
    return await call_next(request)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Execute actions on application startup."""
    print(f"Starting backend API on {settings.HOST}:{settings.PORT}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Execute actions on application shutdown."""
    print("Shutting down backend API")