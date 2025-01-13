from django.urls import path
from .views import SendNotificationView ,DeleteNotificationView , AgentNotificationsView,AgentNotificationHistoryView,AdminPaymentView,AgentTotalPaymentView,PaymentHistoryView
from .views import CreateEventView
from .views import UpdateEventView
from .views import DeleteEventView , ListEventsView
urlpatterns = [
    path('send-notification/', SendNotificationView.as_view(), name='send-notification'),
    path('delete-notification/<int:pk>/', DeleteNotificationView.as_view(), name='delete-notification'),
    path('agent-notifications/<int:agent_id>/', AgentNotificationsView.as_view(), name='agent-notifications'),
    path('notifications/history/', AgentNotificationHistoryView.as_view(), name='notification-history'),
    path('admin/payment/', AdminPaymentView.as_view(), name='admin-payment'),
    path('agent/total-payment/', AgentTotalPaymentView.as_view(), name='agent-total-payment'),
    path('agent/payments/history/', PaymentHistoryView.as_view(), name='payment-history'),
    path('create-event/', CreateEventView.as_view(), name='create-event'),
    path('events/<int:pk>/update/', UpdateEventView.as_view(), name='update-event'),
    path('events/<int:pk>/delete/', DeleteEventView.as_view(), name='delete_event'),
    path('events/', ListEventsView.as_view(), name='list_events'),
]


