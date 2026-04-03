from __future__ import annotations

from django.conf import settings
from rest_framework import serializers

from apps.rag.security.metadata_filter import MetadataSecurityFilter


class RagQuerySerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=8000)
    tenant_id = serializers.CharField(required=False, allow_blank=True)
    top_k = serializers.IntegerField(required=False, min_value=1)
    filters = serializers.DictField(required=False)

    def validate(self, attrs):
        attrs["tenant_id"] = attrs.get("tenant_id") or settings.RAG_DEFAULT_TENANT_ID
        attrs["filters"] = MetadataSecurityFilter.sanitize(attrs.get("filters", {}))

        prompt = (attrs.get("prompt") or "").strip()
        if not prompt:
            raise serializers.ValidationError({"prompt": "prompt cannot be blank."})

        attrs["prompt"] = prompt
        return attrs


class RagQueryResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    contexts = serializers.ListField(child=serializers.CharField())
    references = serializers.ListField(child=serializers.DictField())
