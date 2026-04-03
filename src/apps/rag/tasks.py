from __future__ import annotations

import logging

from celery import shared_task
from django.db import transaction

from apps.rag.models import IngestionJob, RagChunk
from apps.rag.services.ingestion_service import IngestionService

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3}, retry_backoff=True)
def process_ingestion_job(self, job_id: str):
    try:
        job = IngestionJob.objects.get(id=job_id)
    except IngestionJob.DoesNotExist:
        logger.error("RAG ingestion job not found: %s", job_id)
        return

    service = IngestionService()

    try:
        service.process_job(job)
    except Exception as exc:
        logger.exception("RAG ingestion failed for job=%s", job_id)
        service.fail_job(job, exc)
        raise


@shared_task(bind=True)
def mark_stale_embeddings(self, tenant_id: str, target_model: str, target_version: str) -> int:
    stale_qs = RagChunk.objects.filter(
        tenant_id=tenant_id,
    ).exclude(
        embedding_model=target_model,
        embedding_model_version=target_version,
    )
    return stale_qs.update(is_stale=True)
