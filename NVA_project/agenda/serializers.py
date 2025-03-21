from rest_framework import serializers
from event.models import Event
from .models import AgentAvailability, AgentPreference

class EventForAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'location', 'company_name', 'event_code', 'start_date', 'end_date']

class AgentAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentAvailability
        fields = ['id', 'date', 'is_available', 'note', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class AgentPreferenceSerializer(serializers.ModelSerializer):
    preferred_locations_list = serializers.SerializerMethodField()
    preferred_event_types_list = serializers.SerializerMethodField()
    
    class Meta:
        model = AgentPreference
        fields = [
            'id', 'preferred_locations', 'preferred_event_types', 
            'max_events_per_week', 'max_events_per_month', 
            'preferred_locations_list', 'preferred_event_types_list',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_preferred_locations_list(self, obj):
        if obj.preferred_locations:
            return [location.strip() for location in obj.preferred_locations.split(',')]
        return []
    
    def get_preferred_event_types_list(self, obj):
        if obj.preferred_event_types:
            return [event_type.strip() for event_type in obj.preferred_event_types.split(',')]
        return []

class AgendaMonthSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    days = serializers.ListField(child=serializers.DictField())