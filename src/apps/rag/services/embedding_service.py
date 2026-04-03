from __future__ import annotations

import re

from django.conf import settings

from apps.rag.services.model_clients import ModelClients


class EmbeddingService:
    _CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")

    def __init__(self) -> None:
        self._active_model_name = settings.RAG_EMBEDDING_MODEL
        self.client = ModelClients.embeddings(model=self._active_model_name)

    def _embedding_model_candidates(self) -> list[str]:
        configured = (settings.RAG_EMBEDDING_MODEL or "").strip()
        normalized = configured.split("/", 1)[1] if configured.startswith("models/") else configured

        candidates = [
            configured,
            normalized,
            "gemini-embedding-001",
            "gemini-embedding-2-preview",
            "text-embedding-004",
            "embedding-001",
        ]

        unique: list[str] = []
        for model in candidates:
            if model and model not in unique:
                unique.append(model)
        return unique

    def _should_try_next_model(self, exc: Exception) -> bool:
        message = str(exc).lower()
        return (
            "not found" in message
            or "not supported" in message
            or "404" in message
        )

    def _with_embedding_fallback(
        self,
        *,
        texts: list[str] | None = None,
        query: str | None = None,
        output_dimensionality: int | None = None,
    ):
        models = self._embedding_model_candidates()
        last_error: Exception | None = None

        for idx, model_name in enumerate(models):
            try:
                if model_name != self._active_model_name:
                    self.client = ModelClients.embeddings(model=model_name)
                    self._active_model_name = model_name

                if texts is not None:
                    return self.client.embed_documents(
                        texts,
                        output_dimensionality=output_dimensionality,
                    )
                return self.client.embed_query(
                    query or " ",
                    output_dimensionality=output_dimensionality,
                )
            except Exception as exc:
                last_error = exc
                if idx < len(models) - 1 and self._should_try_next_model(exc):
                    continue
                raise

        if last_error:
            raise last_error
        return [] if texts is not None else []

    @classmethod
    def _normalize_text(cls, text: str) -> str:
        raw = (text or "")
        normalized = raw.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
        normalized = cls._CONTROL_CHARS_RE.sub(" ", normalized)
        normalized = normalized.replace("\u2028", " ").replace("\u2029", " ")
        normalized = normalized.strip()
        return normalized

    def embed_texts(self, texts: list[str], output_dimensionality: int | None = None) -> list[list[float]]:
        if not texts:
            return []
        sanitized = [self._normalize_text(text) or " " for text in texts]
        return self._with_embedding_fallback(
            texts=sanitized,
            output_dimensionality=output_dimensionality,
        )

    def embed_query(self, query: str, output_dimensionality: int | None = None) -> list[float]:
        return self._with_embedding_fallback(
            query=self._normalize_text(query) or " ",
            output_dimensionality=output_dimensionality,
        )

    def active_model(self) -> tuple[str, str]:
        return self._active_model_name, settings.RAG_EMBEDDING_MODEL_VERSION
