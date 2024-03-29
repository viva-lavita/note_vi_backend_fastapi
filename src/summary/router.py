import logging

from fastapi import (
    APIRouter, Depends, HTTPException, Request, status,
    UploadFile, File
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.config import current_active_verified_user
from src.auth.models import User
from src.summary.utils import (
    allowed_file, get_file_path, get_filename, save_file, secure_filename
)
from src.database import get_async_session
from src.summary.logic import File as FileLogic


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
    for file in files:
        try:
            if not allowed_file(file.filename):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Недопустимый формат файла {file.filename}'
                )
            safe_filename = secure_filename(file.filename)
            filename = get_filename(safe_filename, user.id)
            file_path = get_file_path(filename, user.id)

            await FileLogic.create(
                session, name=file.filename, path=file_path, user_id=user.id
            )
            await session.commit()

            await save_file(file, filename, user.id)

        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    return {'message': 'Файлы успешно загружены'}
