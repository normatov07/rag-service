# from config.celery import queue
from celery import shared_task
from .file_info_operations import (
    FileInfoWrite as FileInfoWriteTask,
    FileInfoDelete as FileInfoDeleteTask
)

@shared_task(bind=True)
def FileInfoWrite(self, files, model):
    task = FileInfoWriteTask()
    return task.run(files, model)

@shared_task(bind=True)
def FileInfoDelete(self, file_ids):
    task = FileInfoDeleteTask()
    return task.run(file_ids)
