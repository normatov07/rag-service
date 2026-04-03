import hashlib
import re

from django.conf import settings


class CollectionService:
    @staticmethod
    def build_collection_name(tenant_id: str) -> str:
        normalized = re.sub(r"[^a-z0-9_\-]", "-", tenant_id.lower()).strip("-")
        if not normalized:
            normalized = settings.RAG_DEFAULT_TENANT_ID

        if len(normalized) > 48:
            digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:8]
            normalized = f"{normalized[:39]}-{digest}"

        return f"{settings.RAG_VECTOR_COLLECTION_PREFIX}_{normalized}"
