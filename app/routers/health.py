from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Check API health")
async def health_check():
    return {"status": "ok"}
