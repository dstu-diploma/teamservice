from .internal import router as internal_router
from .invite import router as invite_router
from .root import router as root_router
from .mate import router as mate_router
from fastapi import APIRouter

main_router = APIRouter()
main_router.include_router(root_router)
main_router.include_router(invite_router)
main_router.include_router(mate_router)
main_router.include_router(internal_router)
