from fastapi import APIRouter

from project.api.router.client import get_errors_info, get_current_user, get_current_user_token, get_current_api_key

main_client_api_router = APIRouter()

main_client_api_router.include_router(
    router=get_errors_info.api_router,
    prefix="/get_errors_info"
)

main_client_api_router.include_router(
    router=get_current_user.api_router,
    prefix="/get_current_user"
)

main_client_api_router.include_router(
    router=get_current_user_token.api_router,
    prefix="/get_current_user_token"
)

main_client_api_router.include_router(
    router=get_current_api_key.api_router,
    prefix="/get_current_api_key"
)
