from fastapi import APIRouter, status

from shopAPI.models import ApiStatus
from shopAPI.config import settings

status_router = APIRouter(
    tags=["Status"],
)


@status_router.get(
    "/",
    summary="Get the API status.",
    status_code=status.HTTP_200_OK,
)
async def status() -> ApiStatus:
    return ApiStatus(
        name=settings.PROJECT_NAME,
        version=settings.VERSION,
        status="OK",
        message="Visit /swagger for more information.",
    )
