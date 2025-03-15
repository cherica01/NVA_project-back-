from rest_framework import serializers
from .models import Presence, PresencePhoto
from accounts.models import Agent

class PresencePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresencePhoto
        fields = ['id', 'photo', 'uploaded_at']

class PresenceSerializer(serializers.ModelSerializer):
    agent = serializers.StringRelatedField()
    photos = PresencePhotoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Presence
        fields = ['id', 'agent', 'timestamp', 'status', 'latitude', 'longitude', 'location_name', 'notes', 'photos']

class PresenceDetailSerializer(serializers.ModelSerializer):
    agent = serializers.StringRelatedField()
    photos = PresencePhotoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Presence
        fields = ['id', 'agent', 'timestamp', 'status', 'latitude', 'longitude', 'location_name', 'notes', 'photos']

class PresenceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presence
        fields = ['latitude', 'longitude', 'location_name', 'notes']
    
    def create(self, validated_data):
        # L'agent est l'utilisateur authentifié
        agent = self.context['request'].user
        presence = Presence.objects.create(agent=agent, **validated_data)
        return presence

class PresencePhotoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresencePhoto
        fields = ['photo']

class PresenceStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presence
        fields = ['status']
    
    def validate_status(self, value):
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Le statut doit être 'approved' ou 'rejected'.")
        return value