from fastapi import APIRouter

from app.web import web_router

view_router = APIRouter()
view_router.include_router(web_router)
