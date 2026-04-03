from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.conf import settings

from apps.rag.tasks import mark_stale_embeddings
from api.rag.permissions import CanReembedRagPermission
from api.rag.utils import TenantResolver


class ReEmbedAPIView(APIView):
    permission_classes = [CanReembedRagPermission]

    def post(self, request):
        tenant_id = TenantResolver.resolve(
            user=request.user,
            requested_tenant_id=request.data.get("tenant_id"),
        ) or settings.RAG_DEFAULT_TENANT_ID
        task = mark_stale_embeddings.delay(
            tenant_id=tenant_id,
            target_model=settings.RAG_EMBEDDING_MODEL,
            target_version=settings.RAG_EMBEDDING_MODEL_VERSION,
        )
        return Response({"task_id": task.id, "tenant_id": tenant_id}, status=status.HTTP_202_ACCEPTED)
