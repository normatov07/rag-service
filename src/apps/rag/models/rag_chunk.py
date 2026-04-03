from django.db import models

from apps.core.models import TimeModelMixin


class RagChunk(TimeModelMixin):
    document = models.ForeignKey("rag.RagDocument", on_delete=models.CASCADE, related_name="chunks")
    tenant_id = models.CharField(max_length=64, db_index=True)

    chunk_index = models.PositiveIntegerField()
    chunk_text = models.TextField()
    token_count = models.PositiveIntegerField(default=0)

    vector_id = models.CharField(max_length=128, unique=True)
    metadata = models.JSONField(default=dict, blank=True)

    embedding_model = models.CharField(max_length=255)
    embedding_model_version = models.CharField(max_length=64, default="latest")
    embedded_at = models.DateTimeField(blank=True, null=True)
    is_stale = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "do_rag_chunks"
        ordering = ("chunk_index",)
        constraints = [
            models.UniqueConstraint(fields=["document", "chunk_index"], name="uq_rag_chunk_doc_index"),
        ]
        indexes = [
            models.Index(fields=["tenant_id", "is_stale"]),
        ]

    def __str__(self) -> str:
        return f"{self.document_id}:{self.chunk_index}"
