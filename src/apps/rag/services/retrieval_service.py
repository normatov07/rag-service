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
        collection_vector_size = self.qdrant.get_collection_vector_size(collection_name)
        if collection_vector_size is None:
            return []

        target_dimension = settings.RAG_EMBEDDING_DIMENSION
        if collection_vector_size != target_dimension:
            raise ValueError(
                f"Collection '{collection_name}' dimension={collection_vector_size} does not match "
                f"configured RAG_EMBEDDING_DIMENSION={target_dimension}."
            )

        query_vector = self.embedding.embed_query(
            prompt,
            output_dimensionality=target_dimension,
        )

        metadata_filter = MetadataSecurityFilter.sanitize(filters)
        metadata_filter["tenant_id"] = tenant_id

        safe_top_k = max(1, min(top_k or settings.RAG_TOP_K, settings.RAG_MAX_TOP_K))
        hits = self.qdrant.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=max(safe_top_k * 4, safe_top_k),
            metadata_filter=metadata_filter,
        )

        allowed_hits = [
            hit
            for hit in hits
            if MetadataSecurityFilter.is_payload_allowed_for_user(getattr(hit, "payload", {}), user)
        ]
        return allowed_hits[:safe_top_k]
