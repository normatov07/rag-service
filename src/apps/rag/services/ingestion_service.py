from __future__ import annotations

import hashlib
from dataclasses import dataclass
from uuid import uuid4

from django.db import transaction
from django.utils import timezone
from qdrant_client.http.models import PointStruct

from apps.rag.models import IngestionJob, RagChunk, RagDocument
from apps.rag.repositories.qdrant_repository import QdrantRepository
from apps.rag.security.metadata_filter import MetadataSecurityFilter
from apps.rag.services.chunking_service import ChunkingService
from apps.rag.services.collection_service import CollectionService
from apps.rag.services.embedding_service import EmbeddingService


@dataclass
class IngestionPayload:
    source_type: str
    tenant_id: str
    metadata: dict
    source: str
    url: str | None
    url_unique_id: str | None
    file_format: str | None
    external_id: int | None
    external_uuid: str | None
    permission: str | None
    department: str | None
    division: str | None
    group_name: str | None
    user_id: int | None
    text_content: str | None = None
    video_transcript: str | None = None


class IngestionService:
    def __init__(self) -> None:
        self.chunking = ChunkingService()
        self.embedding = EmbeddingService()
        self.qdrant = QdrantRepository()

    @staticmethod
    def create_job(payload: dict) -> IngestionJob:
        return IngestionJob.objects.create(
            tenant_id=payload["tenant_id"],
            source_type=payload["source_type"],
            payload=payload,
            embedding_model=payload["embedding_model"],
            embedding_model_version=payload["embedding_model_version"],
        )

    @transaction.atomic
    def process_job(self, job: IngestionJob) -> IngestionJob:
        payload = job.payload
        tenant_id = payload["tenant_id"]
        collection_name = CollectionService.build_collection_name(tenant_id)

        job.status = IngestionJob.Statuses.PROCESSING
        job.stage = IngestionJob.Stages.EXTRACTING
        job.collection_name = collection_name
        job.started_at = timezone.now()
        job.progress_pct = 5
        job.save(update_fields=["status", "stage", "collection_name", "started_at", "progress_pct", "updated_at"])

        metadata = MetadataSecurityFilter.sanitize(payload.get("metadata"))
        metadata.update(
            {
                "type": payload["source_type"],
                "url": payload.get("url"),
                "url_unique_id": payload.get("url_unique_id"),
                "source": payload.get("source"),
                "format": payload.get("file_format"),
                "id": payload.get("external_id"),
                "uuid": payload.get("external_uuid"),
                "permission": payload.get("permission"),
                "department": payload.get("department"),
                "division": payload.get("division"),
                "group": payload.get("group_name"),
                "user_id": payload.get("user_id"),
                "tenant_id": tenant_id,
            }
        )
        metadata = {k: v for k, v in metadata.items() if v not in (None, "")}

        content_text = (payload.get("text_content") or "").strip()
        if payload["source_type"] == "video":
            job.stage = IngestionJob.Stages.TRANSCRIBING
            job.progress_pct = 20
            job.save(update_fields=["stage", "progress_pct", "updated_at"])
            content_text = (payload.get("video_transcript") or "").strip()

        if not content_text:
            raise ValueError("No extractable content was provided. For video ingestion, provide video_transcript.")

        content_checksum = hashlib.sha256(content_text.encode("utf-8")).hexdigest()

        job.stage = IngestionJob.Stages.CHUNKING
        job.progress_pct = 35
        job.save(update_fields=["stage", "progress_pct", "updated_at"])

        chunks = self.chunking.split(content_text)
        if not chunks:
            raise ValueError("Unable to generate chunks from content.")

        job.total_chunks = len(chunks)
        job.save(update_fields=["total_chunks", "updated_at"])

        job.stage = IngestionJob.Stages.EMBEDDING
        job.progress_pct = 55
        job.save(update_fields=["stage", "progress_pct", "updated_at"])

        vectors = self.embedding.embed_texts(chunks)
        vector_size = len(vectors[0])
        self.qdrant.ensure_collection(collection_name=collection_name, vector_size=vector_size)

        embedding_model, embedding_model_version = self.embedding.active_model()

        doc = RagDocument.objects.create(
            tenant_id=tenant_id,
            source_type=payload["source_type"],
            source=payload.get("source") or "platform",
            url=payload.get("url"),
            url_unique_id=payload.get("url_unique_id"),
            external_id=payload.get("external_id"),
            external_uuid=payload.get("external_uuid") or None,
            file_format=payload.get("file_format"),
            permission=payload.get("permission"),
            department=payload.get("department"),
            division=payload.get("division"),
            group_name=payload.get("group_name"),
            user_id=payload.get("user_id"),
            metadata=metadata,
            content_checksum=content_checksum,
            content_text=content_text,
            embedding_model=embedding_model,
            embedding_model_version=embedding_model_version,
            embedded_at=timezone.now(),
        )

        points: list[PointStruct] = []
        chunk_models: list[RagChunk] = []

        for idx, chunk in enumerate(chunks):
            vector_id = f"{tenant_id}-{doc.id}-{idx}-{uuid4().hex[:8]}"
            chunk_payload = {
                **metadata,
                "document_id": doc.id,
                "chunk_index": idx,
                "chunk_text": chunk,
            }
            points.append(PointStruct(id=vector_id, vector=vectors[idx], payload=chunk_payload))
            chunk_models.append(
                RagChunk(
                    document=doc,
                    tenant_id=tenant_id,
                    chunk_index=idx,
                    chunk_text=chunk,
                    token_count=max(1, len(chunk.split())),
                    vector_id=vector_id,
                    metadata=chunk_payload,
                    embedding_model=embedding_model,
                    embedding_model_version=embedding_model_version,
                    embedded_at=timezone.now(),
                    is_stale=False,
                )
            )

        job.stage = IngestionJob.Stages.UPSERTING
        job.progress_pct = 80
        job.save(update_fields=["stage", "progress_pct", "updated_at"])

        self.qdrant.upsert_points(collection_name=collection_name, points=points)
        RagChunk.objects.bulk_create(chunk_models)

        job.indexed_chunks = len(chunk_models)
        job.status = IngestionJob.Statuses.COMPLETED
        job.stage = IngestionJob.Stages.DONE
        job.progress_pct = 100
        job.finished_at = timezone.now()
        job.error_code = None
        job.error_message = None
        job.save(
            update_fields=[
                "indexed_chunks",
                "status",
                "stage",
                "progress_pct",
                "finished_at",
                "error_code",
                "error_message",
                "updated_at",
            ]
        )

        return job

    @staticmethod
    def fail_job(job: IngestionJob, error: Exception) -> None:
        job.status = IngestionJob.Statuses.FAILED
        job.error_code = error.__class__.__name__
        job.error_message = str(error)
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "error_code", "error_message", "finished_at", "updated_at"])
