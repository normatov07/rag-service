import uuid

from django.db import models

from apps.core.models import TimeModelMixin


class RagDocument(TimeModelMixin):
    class SourceTypes(models.TextChoices):
        TEXT = "text", "Text"
        FILE = "file", "File"
        VIDEO = "video", "Video"

    tenant_id = models.CharField(max_length=64, db_index=True)
    source_type = models.CharField(max_length=16, choices=SourceTypes.choices)
    source = models.CharField(max_length=128, default="platform")
    url = models.URLField(max_length=1000, blank=True, null=True)
    url_unique_id = models.CharField(max_length=255, blank=True, null=True)

    external_id = models.IntegerField(blank=True, null=True)
    external_uuid = models.UUIDField(blank=True, null=True)

    file_format = models.CharField(max_length=32, blank=True, null=True)
    permission = models.CharField(max_length=128, blank=True, null=True)
    department = models.CharField(max_length=128, blank=True, null=True)
    division = models.CharField(max_length=128, blank=True, null=True)
    group_name = models.CharField(max_length=128, blank=True, null=True, db_column="group")
    user_id = models.IntegerField(blank=True, null=True)

    content_checksum = models.CharField(max_length=64, db_index=True)
    content_text = models.TextField(blank=True, default="")

    embedding_model = models.CharField(max_length=255)
    embedding_model_version = models.CharField(max_length=64, default="latest")
    embedded_at = models.DateTimeField(blank=True, null=True)

    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "do_rag_documents"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["tenant_id", "source_type"]),
            models.Index(fields=["tenant_id", "url_unique_id"]),
            models.Index(fields=["tenant_id", "external_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "url_unique_id"],
                condition=models.Q(url_unique_id__isnull=False),
                name="uq_rag_document_tenant_url_unique_id",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.id}:{self.source_type}"
