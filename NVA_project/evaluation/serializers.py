from rest_framework import serializers
from .models import EventPerformance, MonthlyRanking, AIAnalysis
from event.models import Event
from accounts.models import Agent
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
import datetime

class EventPerformanceSerializer(serializers.ModelSerializer):
    event_id = serializers.PrimaryKeyRelatedField(source='event', queryset=Event.objects.all())
    event_name = serializers.SerializerMethodField()
    
    class Meta:
        model = EventPerformance
        fields = ['id', 'event_id', 'event_name', 'revenue', 'products_sold', 'client_satisfaction', 'notes']
    
    def get_event_name(self, obj):
        return f"{obj.event.company_name} - {obj.event.event_code}"

class AgentPerformanceSerializer(serializers.ModelSerializer):
    clients = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()
    presence_rate = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    satisfaction_score = serializers.SerializerMethodField()  # Ajout du champ

    class Meta:
        model = Agent
        fields = ['id', 'username', 'first_name', 'last_name', 'photo_url', 'location',
                 'clients', 'products', 'events', 'presence_rate', 'revenue', 'score', 'satisfaction_score']  # Ajout de satisfaction_score

    def get_photo_url(self, obj):
        photo = obj.photos.filter(photo_type='profile').first()
        if photo and photo.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(photo.image.url)
        return None
    
    def get_clients(self, obj):
        month = self.context.get('month')
        return Event.objects.filter(
            agents=obj,
            start_date__year=month.year,
            start_date__month=month.month
        ).values('company_name').distinct().count()
    
    def get_products(self, obj):
        month = self.context.get('month')
        events = Event.objects.filter(
            agents=obj,
            start_date__year=month.year,
            start_date__month=month.month
        )
        
        total_products = 0
        for event in events:
            try:
                total_products += event.performance.products_sold
            except EventPerformance.DoesNotExist:
                pass
        
        return total_products
    
    def get_events(self, obj):
        month = self.context.get('month')
        return Event.objects.filter(
            agents=obj,
            start_date__year=month.year,
            start_date__month=month.month
        ).count()
    
    def get_presence_rate(self, obj):
        month = self.context.get('month')
    
        import calendar
        _, days_in_month = calendar.monthrange(month.year, month.month)
        month_end = datetime.date(month.year, month.month, days_in_month)
    
        from presence.models import Presence
    # Compter uniquement les présences avec statut 'approved' ou 'rejected'
        total_days = Presence.objects.filter(
            agent=obj,
            timestamp__date__gte=month,
            timestamp__date__lte=month_end,
            status__in=['approved', 'rejected']
        ).count()
    
        if total_days == 0:
            return 0
    
        present_days = Presence.objects.filter(
            agent=obj,
            timestamp__date__gte=month,
            timestamp__date__lte=month_end,
            status='approved'
        ).count()
    
        return round((present_days / total_days) * 100, 2) if total_days > 0 else 0
    
    def get_revenue(self, obj):
        month = self.context.get('month')
        events = Event.objects.filter(
            agents=obj,
            start_date__year=month.year,
            start_date__month=month.month
        )
        
        total_revenue = 0
        for event in events:
            try:
                total_revenue += float(event.performance.revenue)
            except EventPerformance.DoesNotExist:
                pass
        
        return total_revenue
    
    def get_score(self, obj):
        month = self.context.get('month')
        try:
            ranking = MonthlyRanking.objects.get(
                agent=obj,
                month__year=month.year,
                month__month=month.month
            )
            return ranking.score
        except MonthlyRanking.DoesNotExist:
            return 0

    def get_satisfaction_score(self, obj):
        month = self.context.get('month')
        events = Event.objects.filter(
            agents=obj,
            start_date__year=month.year,
            start_date__month=month.month
        )
        
        total_satisfaction = 0
        valid_events = 0
        
        for event in events:
            try:
                satisfaction = event.performance.client_satisfaction
                if satisfaction > 0:  # Ignorer les scores non évalués (0)
                    total_satisfaction += satisfaction
                    valid_events += 1
            except EventPerformance.DoesNotExist:
                pass
        
        if valid_events == 0:
            return 0
        
        # Calculer la moyenne et arrondir à 2 décimales
        return round(total_satisfaction / valid_events, 2)
class MonthlyRankingSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='agent.username')
    photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MonthlyRanking
        fields = ['id', 'agent', 'agent_name', 'photo_url', 'score', 'rank', 'month']
    
    def get_photo_url(self, obj):
        # Récupérer la photo de profil si elle existe
        photo = obj.agent.photos.filter(photo_type='profile').first()
        if photo and photo.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(photo.image.url)
        return None

class AIAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysis
        fields = ['id', 'month', 'analysis_json', 'created_at']

class PresenceStatSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()
