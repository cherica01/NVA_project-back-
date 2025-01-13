from django.urls import path
from .views import AgentListView ,AddAgentView,AgentLoginView,AgentUpdateView,AgentDeleteView,UserProfileView

urlpatterns = [
    path('agents/', AgentListView.as_view(), name='agent-list'),
    path('add-agent/', AddAgentView.as_view(), name='add-agent'),
    path('login/', AgentLoginView.as_view(), name='agent-login'),
    path('<int:pk>/update/', AgentUpdateView.as_view(), name='agent-update'),
    path('<int:pk>/delete/', AgentDeleteView.as_view(), name='agent-delete'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
