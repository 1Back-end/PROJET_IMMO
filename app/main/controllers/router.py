from fastapi import APIRouter
from .migration_controller import router as migration
from .authentification_controller import router as authentication
from .user_controller import router as user
from .storage_controller import router as storage
from .address_controller import router as address

api_router = APIRouter()

api_router.include_router(migration)
api_router.include_router(authentication)
api_router.include_router(user)
api_router.include_router(storage)
api_router.include_router(address)
