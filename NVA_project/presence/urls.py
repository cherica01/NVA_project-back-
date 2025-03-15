from django.urls import path
from .views import (
    PresenceListView, PresenceDetailView, CreatePresenceView,
    UploadPresencePhotoView, UpdatePresenceStatusView, 
    PresenceDashboardView, AgentPresencesView
)

urlpatterns = [
    path('', PresenceListView.as_view(), name='presence-list'),
    path('<int:pk>/', PresenceDetailView.as_view(), name='presence-detail'),
    path('create/', CreatePresenceView.as_view(), name='create-presence'),
    path('<int:presence_id>/upload-photo/', UploadPresencePhotoView.as_view(), name='upload-presence-photo'),
    path('<int:presence_id>/update-status/', UpdatePresenceStatusView.as_view(), name='update-presence-status'),
    path('dashboard/', PresenceDashboardView.as_view(), name='presence-dashboard'),
    path('agent/', AgentPresencesView.as_view(), name='agent-presences'),
]