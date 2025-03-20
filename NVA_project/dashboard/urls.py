from django.urls import path
from .views import (
    AdminDashboardStatsView,
    RecentEventsView,
    RecentPaymentsView,
    PaymentChartDataView,
    
)

urlpatterns = [
    path('admin/stats/', AdminDashboardStatsView.as_view(), name='admin-dashboard-stats'),
    path('admin/recent-events/', RecentEventsView.as_view(), name='admin-recent-events'),
    path('admin/recent-payments/', RecentPaymentsView.as_view(), name='admin-recent-payments'),
    path('admin/payment-chart/', PaymentChartDataView.as_view(), name='admin-payment-chart'),
 
]