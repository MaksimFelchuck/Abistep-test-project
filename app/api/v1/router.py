from fastapi import APIRouter
from .endpoints import users, transfers


router = APIRouter()
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(transfers.router, prefix="/transfer", tags=["transfers"])
