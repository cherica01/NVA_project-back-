from rest_framework import serializers
from accounts.models import Agent
from event.models import Event
from payment.models import Payment
from presence.models import Presence
from notification.models import Notification
from messaging.models import Conversation, Message

class DashboardStatsSerializer(serializers.Serializer):
    total_agents = serializers.IntegerField()
    active_agents = serializers.IntegerField()
    total_events = serializers.IntegerField()
    ongoing_events = serializers.IntegerField()
    upcoming_events = serializers.IntegerField()
    total_payments = serializers.DecimalField(max_digits=10, decimal_places=2)
    presence_rate = serializers.FloatField()
    unread_notifications = serializers.IntegerField()
    unread_messages = serializers.IntegerField()

class RecentEventSerializer(serializers.ModelSerializer):
    agent_count = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = ['id', 'location', 'company_name', 'event_code', 'start_date', 'end_date', 'agent_count', 'status']
    
    def get_agent_count(self, obj):
        return obj.agents.count()
    
    def get_status(self, obj):
        import datetime
        now = datetime.datetime.now()
        if obj.start_date > now:
            return "upcoming"
        elif obj.end_date < now:
            return "completed"
        else:
            return "ongoing"

class RecentPaymentSerializer(serializers.ModelSerializer):
    agent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = ['id', 'agent', 'agent_name', 'amount', 'work_days', 'created_at']
    
    def get_agent_name(self, obj):
        return obj.agent.username if obj.agent else "Agent inconnu"

class AgentStatsSerializer(serializers.ModelSerializer):
    event_count = serializers.SerializerMethodField()
    presence_count = serializers.SerializerMethodField()
    total_earnings = serializers.SerializerMethodField()
    
    class Meta:
        model = Agent
        fields = ['id', 'username', 'date_joined', 'event_count', 'presence_count', 'total_earnings']
    
    def get_event_count(self, obj):
        return obj.events.count()
    
    def get_presence_count(self, obj):
        return Presence.objects.filter(agent=obj).count()
    
    def get_total_earnings(self, obj):
        payments = Payment.objects.filter(agent=obj)
        return sum(payment.amount for payment in payments)