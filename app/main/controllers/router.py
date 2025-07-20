from fastapi import APIRouter
from .migration_controller import router as migration
from .authentification_controller import router as authentication
from .user_controller import router as user
from .storage_controller import router as storage
from .address_controller import router as address
from .services_controller import router as services
from .organisation_controller import  router as organisation
from .license_requests_controller import  router as license_requests
from .licence_controller import router as licence
from .licence_duration_controller import router as licence_duration
from .statictics_controller import router as statictics
from .licence_response_service_controller import  router as licence_response_service
from .country_with_city_controller import router as country_with_citys
api_router = APIRouter()

api_router.include_router(migration)
api_router.include_router(licence_duration)
api_router.include_router(licence_response_service)
api_router.include_router(statictics)
api_router.include_router(authentication)
api_router.include_router(user)
api_router.include_router(storage)
api_router.include_router(address)
api_router.include_router(services)
api_router.include_router(organisation)
api_router.include_router(license_requests)
api_router.include_router(licence)
api_router.include_router(country_with_citys)
