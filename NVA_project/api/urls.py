from django.urls import path,include
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    # Autres URLs de votre application
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/', include('accounts.urls')),
    path('management/', include('management.urls')),
    
]
