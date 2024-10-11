from fastapi import APIRouter, status

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.get("/", summary="Not implemented yet.", status_code=status.HTTP_200_OK)
async def foo() -> str:
    return "Not implemented yet."
