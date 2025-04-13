"""
Health check route for the backend service.
"""
from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/ping")
async def ping():
    """
    Health check endpoint that returns a simple status.
    """
    return {"status": "ok", "service": "splitter-backend"}