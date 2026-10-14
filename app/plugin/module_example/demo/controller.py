from fastapi import APIRouter

DemoRouter = APIRouter(prefix="/demo", tags=["示例插件"])


@DemoRouter.get("/ping")
async def plugin_ping():
    return {"plugin": "module_example", "message": "ok"}
