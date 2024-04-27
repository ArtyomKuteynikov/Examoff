import time

from celery import Celery
from docx import Document

from celery.utils.log import get_task_logger

app = Celery('tasks',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0')

app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
    worker_hijack_root_logger=False,
    worker_redirect_stdouts_level='INFO'
)

logger = get_task_logger(__name__)


@app.task
def generate_report_task(arg1, arg2):
    logger.info("Start generating report")
    my_document = Document()
    my_document.save('document.docx')
    time.sleep(10)
    logger.info("Report generated")
