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
from src.summary.utils import (
    allowed_file, allowed_type_summary, get_file_path, get_filename, save_file, secure_filename
)
from src.database import get_async_session
from src.summary.constants import FilesNotFoundError, SummaryNotFoundError
from src.summary.dependencies import valid_user_id, valid_username
from src.summary.logic import File as FileLogic, Summary as SummaryLogic
from src.summary.schemas import FileOut, File as FileSchema, Summary as SummarySchema


logger = logging.getLogger('root')

router_summary = APIRouter(prefix='/summary', tags=['summary'])


# TODO: файл сохраняется с новым названием
# TODO: новое название делаем путем пропуска старого названия через функцию безопасной обработки
# TODO: старое название сохраняем к файлу в таблицу File в поле name (потом понадобиться в случае восстановления)
# TODO: путь к новому файлу(включая новое название + относительный главной папке путь) сохраняем в таблицу File в поле path

@router_summary.post('/upload')
async def upload(
    files: list[UploadFile] = File(...),
    user: User = Depends(current_active_verified_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Загрузка файлов. Файлы загружаются в папку пользователя.
    """
    for file in files:
        if not allowed_file(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Недопустимый формат файла {file.filename}'
            )
        safe_filename = secure_filename(file.filename)
        filename = get_filename(safe_filename, user.id)
        file_path = get_file_path(filename, user.id)
        try:
            new_file = await FileLogic.create(
                session, name=file.filename, path=file_path, user_id=user.id
            )
            await session.commit()
            FileLogic.get(session, new_file.id)
            await save_file(file, filename, user.id)

        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    return {'message': 'Файлы успешно загружены'}


@router_summary.get('/get_files')
async def get_files(
    id: UUID | None = None,
    username: str | None = None,
    user: User = Depends(current_active_verified_user),
    session: AsyncSession = Depends(get_async_session)
) -> FileSchema | list[FileSchema]:
    """
    Получение файлов.

    Если не указано ни одного параметра, то возвращаются все файлы пользователя.
    Если указан параметр id, то возвращается только один файл с указанным id,
    если он принадлежит пользователю.
    Если указан параметр username, то возвращаются все файлы пользователя
    с указанным username.
    """
    if id:
        file = await FileLogic.get(session, id)
        if not file:
            raise HTTPException(
                status_code=FilesNotFoundError.status_code,
                detail=FilesNotFoundError.description
            )
        in_user = await UserLogic.get(session, 'id', file.user_id)
        if in_user != user:
            raise HTTPException(
                status_code=FilesNotFoundError.status_code,
                detail=FilesNotFoundError.description
            )
        return file
    if username:
        files = await FileLogic.get_list_by_username(session, username)
        if not files:
            raise HTTPException(
                status_code=FilesNotFoundError.status_code,
                detail=FilesNotFoundError.description
            )
        return files
    files = await FileLogic.get_list(session, user.id)
    if not files:
        raise HTTPException(
            status_code=FilesNotFoundError.status_code,
            detail=FilesNotFoundError.description
        )
    return files


@router_summary.post('/upload_summary')
async def upload_summary(
    files: list[UploadFile] = File(...),
    user: User = Depends(current_active_verified_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Создание и загрузка конспектов.
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
                author_id=user.id
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


@router_summary.get('/get_summary')
async def get_summary(
    username: Mapping | None = Depends(valid_username),
    user_id: Mapping | None = Depends(valid_user_id),
    is_public: bool | None = None,
    user: User = Depends(current_active_verified_user),
    session: AsyncSession = Depends(get_async_session)
) -> SummarySchema | list[SummarySchema]:
    """
    Получение конспектов.

    Если не указано ни одного параметра, то возвращаются все конспекты
    текущего пользователя.
    Если указан параметр username, то возвращаются все файлы пользователя
    с указанным username.
    Если указан параметр is_public, то возвращаются все конспекты с указанным
    параметром.
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
