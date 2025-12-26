from celery import Celery

from src.config.dependencies import get_settings

settings = get_settings()

celery_app = Celery(
    "online_cinema_fastapi",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(timezone="UTC", enable_utc=True)

celery_app.autodiscover_tasks(["src.tasks"])

celery_app.conf.beat_schedule = settings.CELERY_BEAT_SCHEDULE
