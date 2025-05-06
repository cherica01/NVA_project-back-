from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EventPerformanceViewSet,
    get_agent_performances,
    get_monthly_rankings,
    get_presence_stats,
    get_ai_analysis,
    calculate_monthly_rankings,
    export_performance_csv
)

router = DefaultRouter()
router.register(r'performances', EventPerformanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('agent-performances/', get_agent_performances, name='agent-performances'),
    path('rankings/', get_monthly_rankings, name='monthly-rankings'),
    path('presence-stats/', get_presence_stats, name='presence-stats'),
    path('ai-analysis/', get_ai_analysis, name='ai-analysis'),
    path('calculate-rankings/', calculate_monthly_rankings, name='calculate-rankings'),
    path('export-csv/', export_performance_csv, name='export-csv'),
]
