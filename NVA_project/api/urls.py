from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    # URLs pour l'authentification JWT
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    
    # URLs pour la gestion des agents (déjà existant)
    path('accounts/', include('accounts.urls')),
    
    # Nouvelles URLs pour chaque application
    path('event/', include('event.urls')),
    path('payment/', include('payment.urls')),
    path('notification/', include('notification.urls')),
    path('messaging/',include('messaging.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('agenda/', include('agenda.urls')),
    path('presence/', include('presence.urls')),
    path('evaluation/', include('evaluation.urls')),
   
]