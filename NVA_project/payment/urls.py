from django.urls import path
from .views import (
    PaymentListView, PaymentDetailView, CreatePaymentView,
    AgentPaymentsView, AgentTotalPaymentView
)

urlpatterns = [
    path('', PaymentListView.as_view(), name='payment-list'),
    path('<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('create/', CreatePaymentView.as_view(), name='create-payment'),
    path('agent/', AgentPaymentsView.as_view(), name='agent-payments'),
    path('agent/<int:agent_id>/', AgentPaymentsView.as_view(), name='specific-agent-payments'),
    path('agent/<int:agent_id>/total/', AgentTotalPaymentView.as_view(), name='agent-total-payment'),
    path('agent/total/', AgentTotalPaymentView.as_view(), name='current-agent-total-payment'),
]