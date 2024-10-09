from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# Add this line to explicitly set the retry on startup
celery_app.conf.update(
    broker_connection_retry_on_startup=True
)

import cel.tasks

# sudo service redis-server start
# celery -A cel.celery_app worker --loglevel=info --pool=solo.