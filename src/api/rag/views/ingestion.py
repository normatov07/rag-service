from rest_framework import status
from rest_framework.response import Response

from apps.rag.models import IngestionJob
from apps.rag.services.ingestion_service import IngestionService
from apps.rag.tasks import process_ingestion_job
from config.views import BasePermissionModelViewSet
from api.rag.serializers.ingestion import IngestionCreateSerializer, IngestionJobSerializer
from api.rag.utils import TenantResolver


class IngestionViewSet(BasePermissionModelViewSet):
    required_permissions = {
        "create": ["can_rag_ingest_manage"],
        "retrieve": ["can_rag_ingest_view"],
        "list": ["can_rag_ingest_view"],
    }
    queryset = IngestionJob.objects.all()
    serializer_class = IngestionJobSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        queryset = super().get_queryset()

        tenant_id = TenantResolver.resolve(
            user=self.request.user,
            requested_tenant_id=self.request.query_params.get("tenant_id"),
        )
        queryset = queryset.filter(tenant_id=tenant_id)

        return queryset.order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = IngestionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = IngestionService()
        payload = dict(serializer.validated_data)
        payload.pop("file", None)
        payload["tenant_id"] = TenantResolver.resolve(
            user=request.user,
            requested_tenant_id=payload.get("tenant_id"),
        )
        job = service.create_job(payload=payload)
        async_result = process_ingestion_job.delay(str(job.id))

        job.celery_task_id = async_result.id
        job.save(update_fields=["celery_task_id", "updated_at"])

        return Response(IngestionJobSerializer(job).data, status=status.HTTP_202_ACCEPTED)
