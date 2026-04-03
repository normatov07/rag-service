from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.rag.views.ingestion import IngestionViewSet
from api.rag.views.query import RagQueryAPIView
from api.rag.views.reembed import ReEmbedAPIView

router = DefaultRouter()
router.register("ingestions", IngestionViewSet, basename="rag-ingestions")

urlpatterns = [
    path("", include(router.urls)),
    path("query/", RagQueryAPIView.as_view(), name="rag-query"),
    path("reembed/", ReEmbedAPIView.as_view(), name="rag-reembed"),
]
