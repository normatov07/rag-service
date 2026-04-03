import os
from kombu import Queue
from celery import (
    Celery,
    Task
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

queue = Celery('config')

queue.config_from_object('django.conf:settings', namespace='CELERY')

queue.autodiscover_tasks()

queue.conf.task_queues = (
    Queue('do_utg_queue_celery', routing_key='do_utg.#'),
)

queue.conf.task_default_queue = 'do_utg_queue_celery'
queue.conf.task_default_exchange = 'default'
queue.conf.task_default_exchange_type = 'direct'
queue.conf.task_default_routing_key = 'do_utg_queue_celery'

class CeleryBaseTask(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 5}
    # retry_backoff = True # exponential retry delay in second
    retry_jitter = False
    default_retry_delay = 5
    store_errors_even_if_ignored = True
    