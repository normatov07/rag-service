# RAG Module Specification

## Overview
This module provides reusable Retrieval-Augmented Generation (RAG) capabilities for platform services.

## Architecture
- `apps.rag`: domain models, ingestion/retrieval/generation services, qdrant repository, celery tasks.
- `api.rag`: DRF endpoints, serializers, validators.
- Vector store: Qdrant Cloud API.
- Models: Google Gemini API
  - LLM: `gemini-2.5-flash`
  - Embedding: `gemini-embedding-001`

## Multi-Tenant Strategy
- Collection per tenant, resolved by: `RAG_VECTOR_COLLECTION_PREFIX + tenant_id`.
- Tenant fallback: `RAG_DEFAULT_TENANT_ID`.
- Retention policy: keep forever.

## Security
- Metadata sanitization allow-list.
- User scope enforced through metadata filter (`department`, `division`, `group`, `user_id`).
- DRF throttling and bounded `top_k`.

## Model Versioning
- `RagDocument` and `RagChunk` store `embedding_model` and `embedding_model_version`.
- `mark_stale_embeddings` task marks vectors stale when model version drifts.
