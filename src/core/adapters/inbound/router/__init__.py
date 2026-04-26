"""ライバー API のルーター群を集約する。"""

from fastapi import APIRouter

from core.adapters.inbound.router.get_liver import router as get_liver_router
from core.adapters.inbound.router.get_liver_color import (
    router as get_liver_color_router,
)
from core.adapters.inbound.router.list_livers import router as list_livers_router
from core.adapters.inbound.router.search_livers import router as search_livers_router

livers_router = APIRouter(prefix="/v1", tags=["livers"])
livers_router.include_router(list_livers_router)
livers_router.include_router(search_livers_router)
livers_router.include_router(get_liver_router)
livers_router.include_router(get_liver_color_router)

__all__ = ["livers_router"]