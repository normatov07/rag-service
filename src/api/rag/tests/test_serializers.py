from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings

from api.rag.serializers.ingestion import IngestionCreateSerializer
from api.rag.serializers.query import RagQuerySerializer


@override_settings(RAG_DEFAULT_TENANT_ID="default-tenant")
class IngestionSerializerTests(SimpleTestCase):
    def test_text_ingestion_requires_text_content(self):
        serializer = IngestionCreateSerializer(
            data={
                "source_type": "text",
                "text_content": "",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("text_content", serializer.errors)

    def test_text_ingestion_applies_tenant_default_and_metadata_sanitization(self):
        serializer = IngestionCreateSerializer(
            data={
                "source_type": "text",
                "text_content": "hello world",
                "metadata": {
                    "department": "DEP-1",
                    "unknown": "drop",
                },
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["tenant_id"], "default-tenant")
        self.assertEqual(serializer.validated_data["metadata"], {"department": "DEP-1"})

    def test_file_ingestion_derives_file_format(self):
        file_obj = SimpleUploadedFile("doc.txt", b"sample text content", content_type="text/plain")
        serializer = IngestionCreateSerializer(
            data={
                "source_type": "file",
                "file": file_obj,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["file_format"], "txt")


@override_settings(RAG_DEFAULT_TENANT_ID="default-tenant")
class QuerySerializerTests(SimpleTestCase):
    def test_query_serializer_sanitizes_filters(self):
        serializer = RagQuerySerializer(
            data={
                "prompt": "What is policy?",
                "filters": {
                    "department": "DEP-2",
                    "bad_key": "bad",
                },
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["tenant_id"], "default-tenant")
        self.assertEqual(serializer.validated_data["filters"], {"department": "DEP-2"})
