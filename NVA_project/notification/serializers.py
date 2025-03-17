from rest_framework import serializers
from .models import Notification
from accounts.models import Agent

class NotificationSerializer(serializers.ModelSerializer):
    recipient = serializers.StringRelatedField()
    
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'message', 'date', 'is_read', 'created_at']

class NotificationCreateSerializer(serializers.ModelSerializer):
    recipient_id = serializers.IntegerField()
    
    class Meta:
        model = Notification
        fields = ['recipient_id', 'message', 'date']
    
    def validate_recipient_id(self, value):
        try:
            Agent.objects.get(id=value)
        except Agent.DoesNotExist:
            raise serializers.ValidationError("Agent non trouvé.")
        return value
    
    def create(self, validated_data):
        recipient_id = validated_data.pop('recipient_id')
        recipient = Agent.objects.get(id=recipient_id)
        notification = Notification.objects.create(recipient=recipient, **validated_data)
        return notification