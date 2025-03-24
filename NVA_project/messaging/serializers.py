from rest_framework import serializers
from accounts.models import Agent
from .models import Conversation, Message

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_agent']

class MessageSerializer(serializers.ModelSerializer):
    sender = AgentSerializer(read_only=True)
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'content', 'created_at', 'is_read']
    
    def get_sender_name(self, obj):
        return obj.sender.username

class ConversationSerializer(serializers.ModelSerializer):
    participants = AgentSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at', 'updated_at', 'last_message', 'unread_count']
    
    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return {
                'id': last_message.id,
                'content': last_message.content,
                'sender': last_message.sender.username,
                'created_at': last_message.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        user = self.context.get('request').user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()

class ConversationCreateSerializer(serializers.Serializer):
    participants = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    
    def validate_participants(self, value):
        # Vérifier que tous les participants existent
        for user_id in value:
            try:
                Agent.objects.get(id=user_id)
            except Agent.DoesNotExist:
                raise serializers.ValidationError(f"L'agent avec l'ID {user_id} n'existe pas.")
        return value
    
    def create(self, validated_data):
        participants_ids = validated_data.get('participants')
        # Ajouter l'utilisateur actuel aux participants
        current_user = self.context.get('request').user
        participants_ids.append(current_user.id)
        # Supprimer les doublons
        participants_ids = list(set(participants_ids))
        
        # Créer la conversation
        conversation = Conversation.objects.create()
        # Ajouter les participants
        for user_id in participants_ids:
            user = Agent.objects.get(id=user_id)
            conversation.participants.add(user)
        
        return conversation

class MessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField()
    
    def create(self, validated_data):
        conversation_id = self.context.get('conversation_id')
        sender = self.context.get('request').user
        
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise serializers.ValidationError("La conversation n'existe pas.")
        
        # Vérifier que l'utilisateur est un participant de la conversation
        if sender not in conversation.participants.all():
            raise serializers.ValidationError("Vous n'êtes pas un participant de cette conversation.")
        
        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=validated_data.get('content')
        )
        
        # Mettre à jour la date de mise à jour de la conversation
        conversation.save()  # auto_now=True mettra à jour updated_at
        
        return message

