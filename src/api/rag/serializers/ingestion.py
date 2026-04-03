from __future__ import annotations

from django.conf import settings
from rest_framework import serializers

from apps.rag.models import IngestionJob
from apps.rag.security.metadata_filter import MetadataSecurityFilter
from apps.rag.services.content_extraction_service import ContentExtractionService
from api.rag.validators.files import RAG_UPLOAD_VALIDATOR


class IngestionCreateSerializer(serializers.Serializer):
    source_type = serializers.ChoiceField(choices=["text", "file", "video"])
    tenant_id = serializers.CharField(required=False, allow_blank=True)

    text_content = serializers.CharField(required=False, allow_blank=True)
    video_transcript = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(required=False, allow_null=True)

    metadata = serializers.DictField(required=False)

    url = serializers.URLField(required=False, allow_blank=True)
    url_unique_id = serializers.CharField(required=False, allow_blank=True)
    source = serializers.CharField(required=False, allow_blank=True, default="platform")
    format = serializers.CharField(required=False, allow_blank=True)
    id = serializers.IntegerField(required=False)
    uuid = serializers.UUIDField(required=False)
    permission = serializers.CharField(required=False, allow_blank=True)
    department = serializers.CharField(required=False, allow_blank=True)
    division = serializers.CharField(required=False, allow_blank=True)
    user_id = serializers.IntegerField(required=False)
    group = serializers.CharField(required=False, allow_blank=True)

    @staticmethod
    def _strip_null_bytes(value: str | None) -> str:
        return (value or "").replace("\x00", "")

    def validate(self, attrs):
        source_type = attrs["source_type"]
        file_obj = attrs.get("file")
        text_content = self._strip_null_bytes(attrs.get("text_content")).strip()
        video_transcript = self._strip_null_bytes(attrs.get("video_transcript")).strip()

        attrs["text_content"] = self._strip_null_bytes(attrs.get("text_content"))
        attrs["video_transcript"] = self._strip_null_bytes(attrs.get("video_transcript"))

        if source_type == "text" and not text_content:
            raise serializers.ValidationError({"text_content": "text_content is required for text ingestion."})

        if source_type in {"file", "video"} and not file_obj and not text_content and not video_transcript:
            raise serializers.ValidationError(
                {"file": "Provide file upload or prepared transcript/text_content for file/video ingestion."}
            )

        if file_obj:
            RAG_UPLOAD_VALIDATOR(file_obj)

        metadata = MetadataSecurityFilter.sanitize(attrs.get("metadata", {}))
        attrs["metadata"] = metadata

        tenant_id = attrs.get("tenant_id") or settings.RAG_DEFAULT_TENANT_ID
        attrs["tenant_id"] = tenant_id

        if file_obj and not text_content:
            extracted = ContentExtractionService.extract_from_upload(
                file_obj=file_obj,
                source_type=source_type,
                video_transcript=video_transcript,
            )
            extracted_text = self._strip_null_bytes(extracted)
            attrs["text_content"] = extracted_text

            file_name = (getattr(file_obj, "name", "") or "").lower()
            is_media = file_name.endswith(".mp4") or file_name.endswith(".mp3") or source_type == "video"
            if is_media and not extracted_text.strip():
                raise serializers.ValidationError(
                    {
                        "video_transcript": (
                            "Transcript is required for media uploads (mp4/mp3). "
                            "Provide video_transcript or text_content."
                        )
                    }
                )

        attrs["embedding_model"] = settings.RAG_EMBEDDING_MODEL
        attrs["embedding_model_version"] = settings.RAG_EMBEDDING_MODEL_VERSION

        attrs["file_format"] = attrs.get("format")
        attrs["external_id"] = attrs.get("id")
        attrs["external_uuid"] = str(attrs.get("uuid")) if attrs.get("uuid") else None
        attrs["group_name"] = attrs.get("group")

        if not attrs.get("format") and file_obj:
            attrs["format"] = str(file_obj.name).split(".")[-1].lower()
            attrs["file_format"] = attrs["format"]

        return attrs


class IngestionJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionJob
        fields = [
            "id",
            "tenant_id",
            "collection_name",
            "source_type",
            "status",
            "stage",
            "progress_pct",
            "total_chunks",
            "indexed_chunks",
            "embedding_model",
            "embedding_model_version",
            "celery_task_id",
            "error_code",
            "error_message",
            "started_at",
            "finished_at",
            "created_at",
            "updated_at",
        ]
