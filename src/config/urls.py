from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),
	path('digital-office/', include(('api.urls.v1', 'api'), namespace='v1')),

    path('digital-office/api/schema/', SpectacularAPIView.as_view(authentication_classes=[]), name='schema'),
    path('digital-office/api/docs/', SpectacularSwaggerView.as_view(url_name='schema', authentication_classes=[]), name='swagger-ui'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)