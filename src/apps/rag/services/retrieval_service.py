from __future__ import annotations

from django.conf import settings

from apps.rag.repositories.qdrant_repository import QdrantRepository
from apps.rag.security.metadata_filter import MetadataSecurityFilter
from apps.rag.services.collection_service import CollectionService
from apps.rag.services.embedding_service import EmbeddingService


class RetrievalService:
    def __init__(self) -> None:
        self.qdrant = QdrantRepository()
        self.embedding = EmbeddingService()

    def retrieve(self, *, tenant_id: str, prompt: str, filters: dict, user: dict, top_k: int):
        collection_name = CollectionService.build_collection_name(tenant_id)
        query_vector = self.embedding.embed_query(prompt)

        metadata_filter = MetadataSecurityFilter.sanitize(filters)
        metadata_filter["tenant_id"] = tenant_id
        metadata_filter = MetadataSecurityFilter.with_user_scope(metadata_filter, user)

        safe_top_k = max(1, min(top_k or settings.RAG_TOP_K, settings.RAG_MAX_TOP_K))
        return self.qdrant.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=safe_top_k,
            metadata_filter=metadata_filter,
        )
