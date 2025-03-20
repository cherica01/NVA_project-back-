from rest_framework import serializers
from .models import Notification
from accounts.models import Agent

class NotificationSerializer(serializers.ModelSerializer):
    recipient = serializers.StringRelatedField()
    
    class Meta:
        model = Notification
        fields = ['id', 'title', 'recipient', 'message', 'is_global', 'is_read', 'date', 'created_at']

class NotificationCreateSerializer(serializers.ModelSerializer):
    recipient_id = serializers.IntegerField(required=False, allow_null=True)
    recipients = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    is_global = serializers.BooleanField(default=False)
    title = serializers.CharField(required=True)
    
    class Meta:
        model = Notification
        fields = ['title', 'recipient_id', 'recipients', 'message', 'date', 'is_global']
    
    def validate(self, data):
        # Si c'est une notification globale, recipient_id n'est pas obligatoire
        if data.get('is_global', False):
            data['recipient_id'] = None
            data['recipients'] = []
            return data
            
        # Si ce n'est pas une notification globale, vérifier qu'il y a au moins un destinataire
        if not data.get('recipient_id') and not data.get('recipients'):
            raise serializers.ValidationError({"recipient_id": "Vous devez spécifier au moins un destinataire pour les notifications non-globales."})
            
        # Vérifier que les agents existent
        if data.get('recipient_id'):
            try:
                Agent.objects.get(id=data['recipient_id'])
            except Agent.DoesNotExist:
                raise serializers.ValidationError({"recipient_id": "Agent non trouvé."})
                
        if data.get('recipients'):
            for agent_id in data['recipients']:
                try:
                    Agent.objects.get(id=agent_id)
                except Agent.DoesNotExist:
                    raise serializers.ValidationError({"recipients": f"Agent avec ID {agent_id} non trouvé."})
            
        return data
    
    def create(self, validated_data):
        is_global = validated_data.pop('is_global', False)
        recipient_id = validated_data.pop('recipient_id', None)
        recipients = validated_data.pop('recipients', [])
        
        notifications = []
        
        # Créer la notification
        if is_global:
            # Notification globale sans destinataire spécifique
            notification = Notification.objects.create(
                recipient=None,
                is_global=True,
                **validated_data
            )
            notifications.append(notification)
        elif recipients:
            # Créer une notification pour chaque destinataire dans la liste
            for agent_id in recipients:
                try:
                    recipient = Agent.objects.get(id=agent_id)
                    notification = Notification.objects.create(
                        recipient=recipient,
                        is_global=False,
                        **validated_data
                    )
                    notifications.append(notification)
                except Agent.DoesNotExist:
                    continue
        else:
            # Notification pour un agent spécifique
            recipient = Agent.objects.get(id=recipient_id)
            notification = Notification.objects.create(
                recipient=recipient,
                is_global=False,
                **validated_data
            )
            notifications.append(notification)
            
        # Retourner la première notification créée (pour compatibilité avec l'API)
        return notifications[0] if notifications else None

