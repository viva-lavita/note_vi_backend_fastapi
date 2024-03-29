import logging
from typing import Mapping
from fastapi import Depends, HTTPException
from pydantic import UUID4

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.logic import UserTokenVerify
from src.auth.constants import RoleNotFoundError, TokenNotFoundError
from src.auth.models import Role
from src.database import get_async_session
from src.exceptions import ObjectNotFoundError
from src.models import get_by_id


logger = logging.getLogger('root')


async def valid_role_id(
        role_id: UUID4,
        session: AsyncSession = Depends(get_async_session)
) -> Mapping:
    try:
        role = await get_by_id(session, Role, role_id)
        return role
    except ObjectNotFoundError:
        logger.warning(f"Role with id {role_id} not found")
        raise HTTPException(
            status_code=RoleNotFoundError.status_code,
            detail=RoleNotFoundError.description
        )
    except Exception as e:
        logger.exception(e)
        return None


async def valid_token(
        token: str,
        session: AsyncSession = Depends(get_async_session)
) -> Mapping:
    try:
        token_instance = await UserTokenVerify.get(session, token)
        return token_instance
    except ObjectNotFoundError:
        logger.warning(f"Token {token} not found")
        raise HTTPException(
            status_code=TokenNotFoundError.status_code,
            detail=TokenNotFoundError.description
        )
    except Exception as e:
        logger.exception(e)
        return None
