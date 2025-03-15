from rest_framework import serializers
from .models import Event
from accounts.models import Agent
from accounts.serializers import AgentSerializers

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'location', 'company_name', 'event_code', 'start_date', 'end_date', 'agents', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['agents'] = instance.agents.values_list('id', flat=True)
        return representation

class EventDetailSerializer(serializers.ModelSerializer):
    agents = AgentSerializers(many=True, read_only=True)
    
    class Meta:
        model = Event
        fields = ['id', 'location', 'company_name', 'event_code', 'start_date', 'end_date', 'agents', 'created_at', 'updated_at']

class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['location', 'company_name', 'event_code', 'start_date', 'end_date', 'agents']
    
    def validate(self, data):
        # Vérifier que la date de fin est après la date de début
        if data['end_date'] <= data['start_date']:
            raise serializers.ValidationError("La date de fin doit être postérieure à la date de début.")
        return data

class AgentEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'location', 'company_name', 'event_code', 'start_date', 'end_date']