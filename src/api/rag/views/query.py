from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.rag.services.generation_service import GenerationService
from apps.rag.services.retrieval_service import RetrievalService
from api.rag.permissions import CanQueryRagPermission
from api.rag.serializers.query import RagQueryResponseSerializer, RagQuerySerializer
from api.rag.utils import TenantResolver


class RagQueryAPIView(APIView):
    permission_classes = [CanQueryRagPermission]

    def post(self, request):
        serializer = RagQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        tenant_id = TenantResolver.resolve(
            user=request.user,
            requested_tenant_id=data.get("tenant_id"),
        )

        retrieval = RetrievalService()
        hits = retrieval.retrieve(
            tenant_id=tenant_id,
            prompt=data["prompt"],
            filters=data.get("filters", {}),
            user=request.user,
            top_k=data.get("top_k"),
        )

        contexts = [hit.payload.get("chunk_text", "") for hit in hits]
        references = [
            {
                "vector_id": hit.id,
                "score": hit.score,
                "document_id": hit.payload.get("document_id"),
                "chunk_index": hit.payload.get("chunk_index"),
                "metadata": {k: v for k, v in hit.payload.items() if k not in {"chunk_text"}},
            }
            for hit in hits
        ]

        generator = GenerationService()
        answer = generator.answer(prompt=data["prompt"], contexts=contexts)

        response = RagQueryResponseSerializer(
            data={
                "answer": answer,
                "contexts": contexts,
                "references": references,
            }
        )
        response.is_valid(raise_exception=True)

        return Response(response.validated_data, status=status.HTTP_200_OK)
