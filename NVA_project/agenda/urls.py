from django.urls import path
from .views import (
    AgentEventsView,
    AgentMonthlyEventsView,
    AgentAvailabilityView,
    AgentAvailabilityDetailView,
    AgentPreferenceView
)

urlpatterns = [
    path('agent/events/', AgentEventsView.as_view(), name='agent-events'),
    path('agent/events/<int:year>/<int:month>/', AgentMonthlyEventsView.as_view(), name='agent-monthly-events'),
    path('agent/availability/', AgentAvailabilityView.as_view(), name='agent-availability'),
    path('agent/availability/<int:pk>/', AgentAvailabilityDetailView.as_view(), name='agent-availability-detail'),
    path('agent/preferences/', AgentPreferenceView.as_view(), name='agent-preferences'),
]