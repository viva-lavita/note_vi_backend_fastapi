import uuid
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend, CookieTransport, JWTStrategy
)

from src.config import config
from src.auth.manager import get_user_manager
from src.auth.models import User


cookie_transport = CookieTransport(cookie_name="Bearer",
                                   cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=config.SECRET_AUTH_KEY,
        lifetime_seconds=60 * 60 * 24 * 7
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_user: User = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True)
current_active_verified_user = fastapi_users.current_user(
    active=True, verified=True
)
current_superuser = fastapi_users.current_user(
    active=True, superuser=True
)
# Использование:
# @app.get("/protected-route")
# def protected_route(user: User = Depends(current_superuser)):
#     return f"Hello, {user.email}"
