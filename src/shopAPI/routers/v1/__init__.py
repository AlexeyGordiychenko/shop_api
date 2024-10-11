from importlib import import_module

from fastapi import APIRouter

router = APIRouter(prefix="/v1")
routes = ("products", "orders")
for module_name in routes:
    api_module = import_module(f"shopAPI.routers.v1.{module_name}")
    api_module_router = api_module.router
    router.include_router(api_module_router)


__all__ = ["router"]
