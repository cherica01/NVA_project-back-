from django.urls import path
from .views import (
    EventListView, EventDetailView, CreateEventView,
    AvailableAgentsView, AgentEventsView, UpdateEventView, DeleteEventView
)

urlpatterns = [
    path('', EventListView.as_view(), name='event-list'),
    path('<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('create/', CreateEventView.as_view(), name='create-event'),
    path('available-agents/', AvailableAgentsView.as_view(), name='available-agents'),
    path('agent/', AgentEventsView.as_view(), name='agent-events'),
    path('update/<int:pk>/', UpdateEventView.as_view(), name='update-event'),
    path('delete/<int:pk>/', DeleteEventView.as_view(), name='delete-event'),
]