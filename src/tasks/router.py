from fastapi import APIRouter, BackgroundTasks, Depends

from src.auth.config import current_user


router_tasks = APIRouter(prefix="/tasks")
