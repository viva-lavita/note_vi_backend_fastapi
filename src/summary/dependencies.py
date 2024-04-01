import logging
from typing import Mapping
from fastapi import Depends, HTTPException, status
from pydantic import UUID4

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.logic import User as UserLogic
from src.auth.models import User
from src.database import get_async_session
from src.exceptions import ObjectNotFoundError
from src.models import get_by_id
from src.summary.constants import SummaryNotFoundError


logger = logging.getLogger('root')


async def valid_username(
        username: str | None = None,
        session: AsyncSession = Depends(get_async_session)
) -> Mapping:
    if username is None:
        return None
    try:
        user = await UserLogic.get(session, "username", username)
        return user.username
    except ObjectNotFoundError:
        logger.info(f"Summary with username {username} not found")
        raise HTTPException(
            status_code=SummaryNotFoundError.status_code,
            detail=SummaryNotFoundError.description
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def valid_user_id(
        user_id: UUID4 | None = None,
        session: AsyncSession = Depends(get_async_session)
) -> Mapping:
    if user_id is None:
        return None
    try:
        user = await get_by_id(session, User, user_id)
        return user.id
    except ObjectNotFoundError:
        logger.info(f"Summary with user_id {user_id} not found")
        raise HTTPException(
            status_code=SummaryNotFoundError.status_code,
            detail=SummaryNotFoundError.description
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
