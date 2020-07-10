from celery import shared_task
from celery.utils.log import get_task_logger
from .models import PlayerMatchSingular

logger = get_task_logger(__name__)


@shared_task()
def process_uploaded_replay(replayFile):
    print(123123)
