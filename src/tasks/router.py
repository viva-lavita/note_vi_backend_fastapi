from fastapi import APIRouter, BackgroundTasks, Depends

from src.auth.config import current_user

from .tasks import send_email_report_dashboard

router_tasks = APIRouter(prefix="/report")


@router_tasks.get("/dashboard")
def get_dashboard_report(background_tasks: BackgroundTasks, user=Depends(current_user)):
    send_email_report_dashboard(user.username)
    background_tasks.add_task(send_email_report_dashboard, user.username)  # это встроенный бэк
    send_email_report_dashboard.delay(user.username)  # это celery задача
    return {
        "status": 200,
        "data": "Письмо отправлено",
        "details": None
    }
