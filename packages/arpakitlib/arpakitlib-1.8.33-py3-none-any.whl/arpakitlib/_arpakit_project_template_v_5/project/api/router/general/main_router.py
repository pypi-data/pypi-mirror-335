from fastapi import APIRouter

from project.api.router.general import healthcheck, now_utc_datetime

main_general_api_router = APIRouter()

main_general_api_router.include_router(
    router=healthcheck.api_router,
    prefix="/healthcheck"
)
main_general_api_router.include_router(
    router=now_utc_datetime.api_router,
    prefix="/now_utc_datetime"
)
