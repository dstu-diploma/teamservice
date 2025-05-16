from .hackathon_teams import router as hackathon_teams_router
from .brand_teams import router as brand_teams_router
from fastapi import APIRouter


router = APIRouter(
    tags=["Админка"],
    prefix="/admin",
)
router.include_router(brand_teams_router)
router.include_router(hackathon_teams_router)
