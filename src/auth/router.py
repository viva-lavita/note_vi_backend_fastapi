from fastapi import APIRouter

from src.auth.shemas import UserCreate, UserRead, UserUpdate
from src.auth.config import auth_backend, fastapi_users

router_auth = APIRouter(prefix="/auth", tags=["auth"])
router_users = APIRouter(prefix="/users", tags=["users"])

router_auth.include_router(
    fastapi_users.get_auth_router(auth_backend)
)
router_auth.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate)
)
router_auth.include_router(
    fastapi_users.get_verify_router(UserRead)
)
router_auth.include_router(
    fastapi_users.get_reset_password_router()
)
router_users.include_router(
    fastapi_users.get_users_router(
        UserRead, UserUpdate, requires_verification=True
    )
)
