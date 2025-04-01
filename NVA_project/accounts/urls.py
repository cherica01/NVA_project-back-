from django.urls import path
from .views import (
    AgentListView, AddAgentView, AgentLoginView, AgentUpdateView, 
    AgentDeleteView, UserProfileView, RegeneratePasswordView,
    AgentPhotoUploadView, AgentPhotoDeleteView
)

urlpatterns = [
    path('agents/', AgentListView.as_view(), name='agent-list'),
    path('add-agent/', AddAgentView.as_view(), name='add-agent'),
    path('login/', AgentLoginView.as_view(), name='agent-login'),
    path('<int:pk>/update/', AgentUpdateView.as_view(), name='agent-update'),
    path('<int:pk>/delete/', AgentDeleteView.as_view(), name='agent-delete'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('regenerate-password/<int:agent_id>/', RegeneratePasswordView.as_view(), name='regenerate-password'),
    path('profile/upload-photo/', AgentPhotoUploadView.as_view(), name='upload-photo'),
    path('profile/delete-photo/<int:photo_id>/', AgentPhotoDeleteView.as_view(), name='delete-photo'),
]

