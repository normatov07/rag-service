from __future__ import annotations

from typing import Any

from django.conf import settings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams, Filter, FieldCondition, MatchValue


class QdrantRepository:
    def __init__(self) -> None:
        api_key = settings.RAG_QDRANT_API_KEY or None
        self.client = QdrantClient(
            url=settings.RAG_QDRANT_URL,
            api_key=api_key,
            timeout=30,
            check_compatibility=False,
        )

    def _create_collection(self, collection_name: str, vector_size: int) -> None:
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    def _collection_vector_size(self, collection_name: str) -> int | None:
        info = self.client.get_collection(collection_name=collection_name)
        vectors = info.config.params.vectors

        if hasattr(vectors, "size") and vectors.size is not None:
            return int(vectors.size)

        if isinstance(vectors, dict) and vectors:
            first = next(iter(vectors.values()))
            if hasattr(first, "size") and first.size is not None:
                return int(first.size)

        return None

    def get_collection_vector_size(self, collection_name: str) -> int | None:
        if not self.client.collection_exists(collection_name=collection_name):
            return None
        return self._collection_vector_size(collection_name=collection_name)

    def ensure_collection(self, collection_name: str, vector_size: int) -> None:
        target_vector_size = int(vector_size)

        if self.client.collection_exists(collection_name=collection_name):
            current_vector_size = self._collection_vector_size(collection_name=collection_name)
            if current_vector_size == target_vector_size:
                return

            raise ValueError(
                f"Qdrant collection '{collection_name}' dimension mismatch: "
                f"existing={current_vector_size}, requested={target_vector_size}."
            )

        self._create_collection(collection_name=collection_name, vector_size=target_vector_size)

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

        if hasattr(self.client, "search"):
            return self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
            )

        response = self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )
        return response.points if hasattr(response, "points") else response
