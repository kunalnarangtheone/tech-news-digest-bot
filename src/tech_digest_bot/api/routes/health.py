"""Health check endpoint."""

from fastapi import APIRouter

from tech_digest_bot.api.models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        Health status of the service
    """
    return HealthResponse(
        status="healthy",
        version="0.4.0",
        services={
            "api": "operational",
            "research": "operational",
        },
    )
