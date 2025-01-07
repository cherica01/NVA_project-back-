from rest_framework import serializers
from .models import Notification, Payment
from .models import Event
from accounts.models import Agent
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['location', 'company_name', 'event_code', 'agents']

class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True) 

    class Meta:
        model = Notification
        fields = ['message', 'date', 'recipient','sender_username']
        
        

class PaymentSerializer(serializers.ModelSerializer):
    total_payment = serializers.FloatField(read_only=True)
    payment_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)  # Format lisible

    class Meta:
        model = Payment
        fields = ['agent', 'work_days', 'amount', 'total_payment', 'payment_date']


class EventSerializer(serializers.ModelSerializer):
    agents = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Agent.objects.all()
    )

    class Meta:
        model = Event
        fields = ['location', 'company_name', 'event_code', 'start_date', 'end_date', 'agents']

    def validate(self, data):
        # Validation de la période
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("La date de début doit être antérieure ou égale à la date de fin.")
        
        # Validation de la disponibilité des agents
        event = self.instance or Event(
            start_date=data.get('start_date', self.instance.start_date if self.instance else None),
            end_date=data.get('end_date', self.instance.end_date if self.instance else None)
        
        )
        unavailable_agents = []
        for agent in data['agents']:
            if not event.is_agent_available(agent):
                unavailable_agents.append(agent.username)
        
        if unavailable_agents:
            raise serializers.ValidationError({
                "agents": f"Les agents suivants ne sont pas disponibles pour cette période : {', '.join(unavailable_agents)}"
            })

        return data
