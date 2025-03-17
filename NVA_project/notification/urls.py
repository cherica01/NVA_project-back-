from django.urls import path
from .views import (
    NotificationListView, NotificationDetailView, SendNotificationView,
    MarkNotificationAsReadView, AgentNotificationsView, UnreadNotificationsCountView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('send/', SendNotificationView.as_view(), name='send-notification'),
    path('<int:notification_id>/mark-as-read/', MarkNotificationAsReadView.as_view(), name='mark-notification-as-read'),
    path('agent/', AgentNotificationsView.as_view(), name='agent-notifications'),
    path('unread-count/', UnreadNotificationsCountView.as_view(), name='unread-notifications-count'),
]