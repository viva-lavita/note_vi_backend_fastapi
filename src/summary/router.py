import logging
from typing import Mapping
from uuid import UUID

from fastapi import (
    APIRouter, Depends, HTTPException, Request, status,
    UploadFile, File
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.config import current_active_verified_user
from src.auth.models import User
from src.auth.logic import User as UserLogic
from src.exceptions import ObjectNotFoundError
from src.summary.utils import (
    allowed_file, allowed_type_image, allowed_type_summary, delete_file,
    get_file_path, get_filename,
    save_file, secure_filename
)
from src.database import get_async_session
from src.summary.constants import FilesNotFoundError, SummaryNotFoundError
from src.summary.dependencies import (
    valid_image_id_obj, valid_summary_id, valid_summary_id_obj,
    valid_user_id, valid_username
)
from src.summary.logic import Summary as SummaryLogic, SummaryImage as SummaryImageLogic
from src.summary.schemas import Summary as SummarySchema, SummaryUpdate


logger = logging.getLogger('root')

router_summary = APIRouter(prefix='/summary', tags=['summary'])


# TODO: файл сохраняется с новым названием
# TODO: новое название делаем путем пропуска старого названия через функцию безопасной обработки
# TODO: старое название сохраняем к файлу в таблицу File в поле name (потом понадобиться в случае восстановления)
# TODO: путь к новому файлу(включая новое название + относительный главной папке путь) сохраняем в таблицу File в поле path


@router_summary.post('/upload')
async def upload_summary(
    files: list[UploadFile] = File(...),
    all_public: bool = False,
    user: User = Depends(current_active_verified_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Создание экземпляра и загрузка конспектов.
    Файлы загружаются в папку id_пользователя/summary/.
    """
    for file in files:
        if not allowed_type_summary(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Недопустимый формат конспекта {file.filename}'
            )
    for file in files:
        safe_filename = secure_filename(file.filename)
        filename = get_filename(safe_filename, user.id, 'summary')
        file_path = get_file_path(filename, user.id, 'summary')
        try:
            new_summary = await SummaryLogic.create(
                session,
                name=file.filename,
                summary_path=file_path,
                author_id=user.id,
                is_public=all_public
            )
            await session.commit()
            await SummaryLogic.get(session, new_summary.id)
            await save_file(file, filename, user.id, 'summary')

        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    return {'message': 'Файлы успешно загружены'}


@router_summary.get('/me')
async def get_summary_me(
    user: User = Depends(current_active_verified_user),
    is_public: bool | None = None,
    session: AsyncSession = Depends(get_async_session)
) -> list[SummarySchema]:
    """
    Получение всех конспектов текущего пользователя.

    Дополнительно можно отфильтровать по is_public.
    """
    return await SummaryLogic.get_list(session, user.id, is_public)


@router_summary.get('/{summary_id}')
async def get_summary_by_id(
    summary_id: UUID,
    user: User = Depends(current_active_verified_user),
    session: AsyncSession = Depends(get_async_session)
) -> SummarySchema:
    """
    Получение конспекта по id.
    """
    try:
        summary = await SummaryLogic.get(session, summary_id)
        return summary
    except ObjectNotFoundError:
        raise HTTPException(
            status_code=SummaryNotFoundError.status_code,
            detail=SummaryNotFoundError.description
        )


@router_summary.get('/')
async def get_summary(
    username: Mapping | None = Depends(valid_username),
    user_id: Mapping | None = Depends(valid_user_id),
    is_public: bool | None = None,
    user: User = Depends(current_active_verified_user),
    session: AsyncSession = Depends(get_async_session)
) -> list[SummarySchema]:
    """
    Получение конспектов.

    Если не указано ни одного параметра, то возвращаются все конспекты.
    Если указан параметр username, то возвращаются все файлы пользователя
    с указанным username.
    Если указан параметр user_id, то возвращаются все файлы пользователя с
    указанным user_id.
    Если указан параметр is_public, то возвращаются все конспекты с указанным
    параметром.
    Можно комбинировать.
    """
    summaries = await SummaryLogic.get_list(
        session, user_id, is_public, username
    )
    if not summaries:
        raise HTTPException(
            status_code=SummaryNotFoundError.status_code,
            detail=SummaryNotFoundError.description
        )
    return summaries


@router_summary.delete('/{summary_id}',
                       status_code=status.HTTP_204_NO_CONTENT)
async def delete_summary(
    summary_id: Mapping = Depends(valid_summary_id),
    user: User = Depends(current_active_verified_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Удаление конспекта по id.
    """
    await SummaryLogic.delete(session, summary_id)
    await session.commit()


@router_summary.patch('/{summary_id}')
async def update_summary(
    new_summary: SummaryUpdate,
    summary: Mapping = Depends(valid_summary_id_obj),
    user: User = Depends(current_active_verified_user),
    session: AsyncSession = Depends(get_async_session)
) -> SummarySchema:
    """
    Обновление конспекта по id.
    """
    if summary.author_id != user.id:
        logger.warning(
            f"User {user.id} tried to update summary {summary.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
        )
    await SummaryLogic.update(session, summary.id, new_summary)
    await session.commit()
    updated_summary = await SummaryLogic.get(session, summary.id)
    return updated_summary


@router_summary.post('/{summary_id}/images')
async def add_images_to_summary(
    summary: Mapping = Depends(valid_summary_id_obj),
    files: list[UploadFile] = File(...),
    user: User = Depends(current_active_verified_user),
    session: AsyncSession = Depends(get_async_session)
) -> SummarySchema:
    """
    Добавление изображений в конспект.
    """
    if summary.author_id != user.id:
        logger.warning(
            f"User {user.id} tried to add images to summary {summary.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
        )
    for file in files:
        if not allowed_type_image(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Invalid image format {file.filename}'
            )
    for file in files:
        safe_filename = secure_filename(file.filename)
        filename = get_filename(safe_filename, user.id, 'image')
        file_path = get_file_path(filename, user.id, 'image')
        try:
            new_image = await SummaryImageLogic.create(
                session, summary.id, file_path
            )
            await session.commit()
            await SummaryImageLogic.get(session, new_image.id)
            await save_file(file, filename, user.id, 'image')
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    return await SummaryLogic.get(session, summary.id)


@router_summary.delete('/{summary_id}/images/{image_id}',
                       status_code=status.HTTP_204_NO_CONTENT)
async def delete_image_from_summary(
    summary_id: Mapping = Depends(valid_summary_id),
    image: Mapping = Depends(valid_image_id_obj),
    user: User = Depends(current_active_verified_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Удаление изображения из конспекта.
    """
    if image.summary.author_id != user.id:
        logger.warning(f"User {user.id} not owner of image {image.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
        )
    await SummaryImageLogic.delete(session, image.id)
    await session.commit()
    await delete_file(image.path)
