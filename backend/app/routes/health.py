from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Simple liveness check — used by deployment platforms (Render) and the frontend."""
    return {"status": "ok"}
