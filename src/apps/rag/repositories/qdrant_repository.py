from __future__ import annotations

from typing import Any

from django.conf import settings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams, Filter, FieldCondition, MatchValue


class QdrantRepository:
    def __init__(self) -> None:
        self.client = QdrantClient(url=settings.RAG_QDRANT_URL, api_key=settings.RAG_QDRANT_API_KEY, timeout=30)

    def ensure_collection(self, collection_name: str, vector_size: int) -> None:
        if self.client.collection_exists(collection_name=collection_name):
            return

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    def upsert_points(self, collection_name: str, points: list[PointStruct]) -> None:
        if points:
            self.client.upsert(collection_name=collection_name, points=points)

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int,
        metadata_filter: dict[str, Any] | None = None,
    ):
        if not self.client.collection_exists(collection_name=collection_name):
            return []

        query_filter = None
        if metadata_filter:
            conditions = [
                FieldCondition(key=key, match=MatchValue(value=value))
                for key, value in metadata_filter.items()
                if value not in (None, "")
            ]
            query_filter = Filter(must=conditions) if conditions else None

        return self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )
