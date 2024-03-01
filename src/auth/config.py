from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend, CookieTransport, JWTStrategy
)

from auth.manager import get_user_manager
from auth.models import User
from src.config import config

cookie_transport = CookieTransport(cookie_name="bonds", cookie_max_age=3600)


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

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()
