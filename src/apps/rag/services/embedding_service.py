from __future__ import annotations

from django.conf import settings

from apps.rag.services.model_clients import ModelClients


class EmbeddingService:
    def __init__(self) -> None:
        self.client = ModelClients.embeddings()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self.client.embed_documents(texts)

    def embed_query(self, query: str) -> list[float]:
        return self.client.embed_query(query)

    @staticmethod
    def active_model() -> tuple[str, str]:
        return settings.RAG_EMBEDDING_MODEL, settings.RAG_EMBEDDING_MODEL_VERSION
