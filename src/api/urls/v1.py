from django.urls import path, include

urlpatterns = [
    path('rag/', include(('api.rag.urls', 'apps.rag'), namespace='rag')),
]