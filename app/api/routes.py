from fastapi import APIRouter

router = APIRouter()


@router.get("/status", summary="API status")
async def status() -> dict[str, str]:
    return {"api": "ready"}