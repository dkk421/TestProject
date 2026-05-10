from celery import Celery

celery_app = Celery(
    "testproject",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
    include=["app.tasks.analytics"],
)