import uuid

from django.db import models

from apps.core.models import TimeModelMixin


class IngestionJob(TimeModelMixin):
    class Statuses(models.TextChoices):
        QUEUED = "queued", "Queued"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class Stages(models.TextChoices):
        RECEIVED = "received", "Received"
        EXTRACTING = "extracting", "Extracting"
        TRANSCRIBING = "transcribing", "Transcribing"
        CHUNKING = "chunking", "Chunking"
        EMBEDDING = "embedding", "Embedding"
        UPSERTING = "upserting", "Upserting"
        DONE = "done", "Done"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=64, db_index=True)
    collection_name = models.CharField(max_length=255, blank=True, null=True)

    source_type = models.CharField(max_length=16, db_index=True)
    status = models.CharField(max_length=16, choices=Statuses.choices, default=Statuses.QUEUED, db_index=True)
    stage = models.CharField(max_length=24, choices=Stages.choices, default=Stages.RECEIVED)

    payload = models.JSONField(default=dict)
    progress_pct = models.PositiveSmallIntegerField(default=0)
    total_chunks = models.PositiveIntegerField(default=0)
    indexed_chunks = models.PositiveIntegerField(default=0)

    embedding_model = models.CharField(max_length=255)
    embedding_model_version = models.CharField(max_length=64, default="latest")

    celery_task_id = models.CharField(max_length=255, blank=True, null=True)
    error_code = models.CharField(max_length=128, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)

    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "do_rag_ingestion_jobs"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["tenant_id", "source_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.id}:{self.status}:{self.stage}"
