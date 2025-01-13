from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]


if settings.DEBUG:  # Assurez-vous que cela ne s'exécute qu'en mode développement
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
