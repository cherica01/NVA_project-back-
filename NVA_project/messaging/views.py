from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from accounts.models import Agent
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, ConversationCreateSerializer,
    MessageSerializer, MessageCreateSerializer,
    AgentSerializer
)

class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Liste toutes les conversations de l'utilisateur authentifié.
        """
        conversations = Conversation.objects.filter(participants=request.user)
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})
        return Response(serializer.data)

class ConversationCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Crée une nouvelle conversation.
        """
        serializer = ConversationCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            conversation = serializer.save()
            return Response(
                ConversationSerializer(conversation, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Récupère les détails d'une conversation spécifique.
        """
        conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data)

class MessageListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, conversation_id):
        """
        Liste tous les messages d'une conversation.
        """
        conversation = get_object_or_404(Conversation, pk=conversation_id, participants=request.user)
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        
        # Marquer les messages non lus comme lus
        unread_messages = messages.filter(is_read=False).exclude(sender=request.user)
        for message in unread_messages:
            message.is_read = True
            message.save()
        
        return Response(serializer.data)
    
    def post(self, request, conversation_id):
        """
        Crée un nouveau message dans une conversation.
        """
        serializer = MessageCreateSerializer(
            data=request.data,
            context={'request': request, 'conversation_id': conversation_id}
        )
        if serializer.is_valid():
            message = serializer.save()
            return Response(
                MessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessageDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Récupère les détails d'un message spécifique.
        """
        message = get_object_or_404(
            Message,
            pk=pk,
            conversation__participants=request.user
        )
        serializer = MessageSerializer(message)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        """
        Supprime un message.
        """
        message = get_object_or_404(
            Message,
            pk=pk,
            sender=request.user
        )
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UnreadMessagesCountView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Récupère le nombre de messages non lus pour l'utilisateur authentifié.
        """
        count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
        
        return Response({'unread_count': count})

class SearchConversationsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Recherche des conversations par nom d'utilisateur.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Paramètre de recherche manquant.'}, status=status.HTTP_400_BAD_REQUEST)
        
        conversations = Conversation.objects.filter(
            participants=request.user,
            participants__username__icontains=query
        ).distinct()
        
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})
        return Response(serializer.data)

class CurrentUserView(APIView):
    """
    Vue pour récupérer les informations de l'utilisateur actuellement connecté
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = AgentSerializer(request.user)
        return Response(serializer.data)

class UsersListView(APIView):
    """
    Vue pour récupérer la liste de tous les utilisateurs
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        users = Agent.objects.all()
        serializer = AgentSerializer(users, many=True)
        return Response(serializer.data)

class AgentsListView(APIView):
    """
    Vue pour récupérer la liste de tous les agents
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        agents = Agent.objects.filter(is_agent=True)
        serializer = AgentSerializer(agents, many=True)
        return Response(serializer.data)

class AdminsListView(APIView):
    """
    Vue pour récupérer la liste de tous les administrateurs
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        admins = Agent.objects.filter(is_staff=True)
        serializer = AgentSerializer(admins, many=True)
        return Response(serializer.data)

