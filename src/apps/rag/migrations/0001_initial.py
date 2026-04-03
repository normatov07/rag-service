# Generated manually for rag app

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="IngestionJob",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("tenant_id", models.CharField(db_index=True, max_length=64)),
                ("collection_name", models.CharField(blank=True, max_length=255, null=True)),
                ("source_type", models.CharField(db_index=True, max_length=16)),
                (
                    "status",
                    models.CharField(
                        choices=[("queued", "Queued"), ("processing", "Processing"), ("completed", "Completed"), ("failed", "Failed")],
                        db_index=True,
                        default="queued",
                        max_length=16,
                    ),
                ),
                (
                    "stage",
                    models.CharField(
                        choices=[
                            ("received", "Received"),
                            ("extracting", "Extracting"),
                            ("transcribing", "Transcribing"),
                            ("chunking", "Chunking"),
                            ("embedding", "Embedding"),
                            ("upserting", "Upserting"),
                            ("done", "Done"),
                        ],
                        default="received",
                        max_length=24,
                    ),
                ),
                ("payload", models.JSONField(default=dict)),
                ("progress_pct", models.PositiveSmallIntegerField(default=0)),
                ("total_chunks", models.PositiveIntegerField(default=0)),
                ("indexed_chunks", models.PositiveIntegerField(default=0)),
                ("embedding_model", models.CharField(max_length=255)),
                ("embedding_model_version", models.CharField(default="latest", max_length=64)),
                ("celery_task_id", models.CharField(blank=True, max_length=255, null=True)),
                ("error_code", models.CharField(blank=True, max_length=128, null=True)),
                ("error_message", models.TextField(blank=True, null=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"db_table": "do_rag_ingestion_jobs", "ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="RagDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("tenant_id", models.CharField(db_index=True, max_length=64)),
                ("source_type", models.CharField(choices=[("text", "Text"), ("file", "File"), ("video", "Video")], max_length=16)),
                ("source", models.CharField(default="platform", max_length=128)),
                ("url", models.URLField(blank=True, max_length=1000, null=True)),
                ("url_unique_id", models.CharField(blank=True, max_length=255, null=True)),
                ("external_id", models.IntegerField(blank=True, null=True)),
                ("external_uuid", models.UUIDField(blank=True, null=True)),
                ("file_format", models.CharField(blank=True, max_length=32, null=True)),
                ("permission", models.CharField(blank=True, max_length=128, null=True)),
                ("department", models.CharField(blank=True, max_length=128, null=True)),
                ("division", models.CharField(blank=True, max_length=128, null=True)),
                ("group_name", models.CharField(blank=True, db_column="group", max_length=128, null=True)),
                ("user_id", models.IntegerField(blank=True, null=True)),
                ("content_checksum", models.CharField(db_index=True, max_length=64)),
                ("content_text", models.TextField(blank=True, default="")),
                ("embedding_model", models.CharField(max_length=255)),
                ("embedding_model_version", models.CharField(default="latest", max_length=64)),
                ("embedded_at", models.DateTimeField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"db_table": "do_rag_documents", "ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="RagChunk",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("tenant_id", models.CharField(db_index=True, max_length=64)),
                ("chunk_index", models.PositiveIntegerField()),
                ("chunk_text", models.TextField()),
                ("token_count", models.PositiveIntegerField(default=0)),
                ("vector_id", models.CharField(max_length=128, unique=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("embedding_model", models.CharField(max_length=255)),
                ("embedding_model_version", models.CharField(default="latest", max_length=64)),
                ("embedded_at", models.DateTimeField(blank=True, null=True)),
                ("is_stale", models.BooleanField(db_index=True, default=False)),
                (
                    "document",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chunks", to="rag.ragdocument"),
                ),
            ],
            options={"db_table": "do_rag_chunks", "ordering": ("chunk_index",)},
        ),
        migrations.AddIndex(model_name="ingestionjob", index=models.Index(fields=["tenant_id", "status"], name="do_rag_inge_tenant__55ebbb_idx")),
        migrations.AddIndex(model_name="ingestionjob", index=models.Index(fields=["tenant_id", "source_type"], name="do_rag_inge_tenant__d4dd6f_idx")),
        migrations.AddIndex(model_name="ragdocument", index=models.Index(fields=["tenant_id", "source_type"], name="do_rag_docu_tenant__65c1f7_idx")),
        migrations.AddIndex(model_name="ragdocument", index=models.Index(fields=["tenant_id", "url_unique_id"], name="do_rag_docu_tenant__4ea436_idx")),
        migrations.AddIndex(model_name="ragdocument", index=models.Index(fields=["tenant_id", "external_id"], name="do_rag_docu_tenant__5f1de5_idx")),
        migrations.AddConstraint(
            model_name="ragdocument",
            constraint=models.UniqueConstraint(
                condition=models.Q(("url_unique_id__isnull", False)),
                fields=("tenant_id", "url_unique_id"),
                name="uq_rag_document_tenant_url_unique_id",
            ),
        ),
        migrations.AddConstraint(
            model_name="ragchunk",
            constraint=models.UniqueConstraint(fields=("document", "chunk_index"), name="uq_rag_chunk_doc_index"),
        ),
        migrations.AddIndex(model_name="ragchunk", index=models.Index(fields=["tenant_id", "is_stale"], name="do_rag_chun_tenant__871403_idx")),
    ]
