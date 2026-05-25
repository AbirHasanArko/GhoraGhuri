"""
GhoraGhuri — Health Check Endpoint
"""
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check for load balancers and monitoring."""
    return {
        "status": "healthy",
        "service": "ghoraghuri-backend",
        "version": "1.0.0",
    }
