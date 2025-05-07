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
from django.conf import settings
import google.generativeai as genai
from django.utils import timezone
from datetime import datetime, timedelta
from agenda.models import Event

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
        agents = Agent.objects.filter(is_staff=False)
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
    
import logging
from .chatbot_utils import (
    format_event_for_display, get_upcoming_events, get_event_details, get_events_by_location, get_next_event,
    get_agent_presence_stats, get_last_presence, get_payment_summary, get_agent_presence_stats,
    get_agent_profile_data, extract_date_range, extract_location, extract_agent_id,
    format_data_for_prompt, get_payment_summary, get_agent_presence_stats, 
)
from .intent_detector import detect_intent

# Configurez le logger
logger = logging.getLogger(__name__)

# Configuration de l'API Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

class ChatbotView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Récupérer le message de l'utilisateur
            user_message = request.data.get('message', '')
            if not user_message:
                return Response({"error": "Message requis"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Récupérer l'utilisateur connecté
            user = request.user
            is_admin = user.is_superuser or user.is_staff
            
            # Détecter l'intention de l'utilisateur
            intent = detect_intent(user_message, is_admin)
            
            # Préparer les données contextuelles selon l'intention
            context_data = {}
            action_required = None
            action_data = {}
            
            # Extraire l'ID de l'agent si mentionné (pour les admins)
            agent_id = None
            if is_admin:
                agent_id = extract_agent_id(user_message)
            
            # Traitement des événements
            if intent == 'events':
                # Extraire la plage de dates si mentionnée
                start_date, end_date = extract_date_range(user_message)
                
                # Extraire l'emplacement si mentionné
                location = extract_location(user_message)
                
                # Rechercher un ID d'événement spécifique
                import re
                event_id_match = re.search(r'événement\s+(\d+)|evenement\s+(\d+)|id\s+(\d+)', user_message.lower())
                
                if event_id_match:
                    # Récupérer les détails d'un événement spécifique
                    event_id = int(next(group for group in event_id_match.groups() if group is not None))
                    event = get_event_details(event_id, user)
                    
                    if event:
                        context_data['event_details'] = format_data_for_prompt(event, 'events')
                        
                        # Préparer l'action pour afficher les détails de l'événement
                        action_required = "show_event"
                        action_data = format_event_for_display(event)
                    else:
                        context_data['event_details'] = f"Aucun événement trouvé avec l'ID {event_id}."
                
                elif "prochain" in user_message.lower() or "suivant" in user_message.lower():
                    # Récupérer le prochain événement
                    next_event = get_next_event(user)
                    if next_event:
                        context_data['next_event'] = format_data_for_prompt(next_event, 'events')
                    else:
                        context_data['next_event'] = "Vous n'avez pas d'événement à venir."
                
                elif location:
                    # Rechercher des événements à un emplacement spécifique
                    location_events = get_events_by_location(user, location)
                    if location_events:
                        context_data['location_events'] = format_data_for_prompt(location_events, 'events')
                    else:
                        context_data['location_events'] = f"Aucun événement trouvé à {location}."
                
                else:
                    # Récupérer les événements à venir (par défaut)
                    days = 7  # Par défaut, une semaine
                    if "mois" in user_message.lower():
                        days = 30
                    
                    upcoming_events = get_upcoming_events(user, days=days)
                    if upcoming_events:
                        context_data['upcoming_events'] = format_data_for_prompt(upcoming_events, 'events')
                    else:
                        context_data['upcoming_events'] = f"Vous n'avez pas d'événements prévus pour les {days} prochains jours."
            
            # Traitement du profil
            elif intent == 'profile':
                if is_admin and agent_id:
                    # Admin demande le profil d'un agent spécifique
                    profile_data = get_agent_profile_data(user, agent_id)
                    if 'error' in profile_data:
                        context_data['profile'] = profile_data['error']
                    else:
                        context_data['profile'] = format_data_for_prompt(profile_data, 'profile')
                else:
                    # Utilisateur demande son propre profil
                    profile_data = get_agent_profile_data(user)
                    context_data['profile'] = format_data_for_prompt(profile_data, 'profile')
            
            # Traitement des présences
            elif intent == 'presence':
                if is_admin:
                    if agent_id:
                        # Admin demande les stats de présence d'un agent spécifique
                        presence_stats = get_agent_presence_stats(user, agent_id)
                        if 'error' in presence_stats:
                            context_data['presence_stats'] = presence_stats['error']
                        else:
                            context_data['presence_stats'] = format_data_for_prompt(presence_stats, 'presence_stats')
                            
                            # Récupérer la dernière présence de cet agent
                            last_presence = get_last_presence(user, agent_id)
                            if last_presence:
                                context_data['last_presence'] = f"Dernière présence de {presence_stats['agent_name']}: {last_presence.timestamp.strftime('%d/%m/%Y à %H:%M')} à {last_presence.location_name}."
                            else:
                                context_data['last_presence'] = f"{presence_stats['agent_name']} n'a pas encore enregistré de présence."
                    else:
                        # Admin demande un résumé des présences de tous les agents
                        all_presence_stats = get_agent_presence_stats(user)
                        context_data['all_presence_stats'] = "Statistiques de présence pour tous les agents:\n"
                        
                        for stats in all_presence_stats:
                            context_data['all_presence_stats'] += f"""
                            - {stats.get('agent_name', 'Nom inconnu') if isinstance(stats, dict) else 'Nom inconnu'}:
                              Total: {stats.get('total', 0) if isinstance(stats, dict) else 0} | Approuvées: {stats.get('approved', 0) if isinstance(stats, dict) else 0} | En attente: {stats.get('pending', 0) if isinstance(stats, dict) else 0} | Rejetées: {stats.get('rejected', 0) if isinstance(stats, dict) else 0}
                            """
                else:
                    # Agent demande ses propres stats de présence
                    presence_stats = get_agent_presence_stats(user)
                    context_data['presence_stats'] = format_data_for_prompt(presence_stats, 'presence_stats')
                    
                    # Récupérer la dernière présence
                    last_presence = get_last_presence(user)
                    if last_presence:
                        context_data['last_presence'] = f"Votre dernière présence a été enregistrée le {last_presence.timestamp.strftime('%d/%m/%Y à %H:%M')} à {last_presence.location_name}."
                    else:
                        context_data['last_presence'] = "Vous n'avez pas encore enregistré de présence."
            
            # Traitement des paiements
            elif intent == 'payments':
                if is_admin and agent_id:
                    # Admin demande les infos de paiement d'un agent spécifique
                    payment_data = get_payment_summary(user, agent_id)
                    if 'error' in payment_data:
                        context_data['payment'] = payment_data['error']
                    else:
                        context_data['payment'] = format_data_for_prompt(payment_data, 'payment')
                else:
                    # Utilisateur demande ses propres infos de paiement
                    payment_data = get_payment_summary(user)
                    context_data['payment'] = format_data_for_prompt(payment_data, 'payment')
            
            # Traitement spécifique pour les admins - liste des agents
            elif intent == 'agents' and is_admin:
                agents_summary = get_payment_summary()
                context_data['agents_summary'] = format_data_for_prompt(agents_summary, 'agents_summary')
            
            # Traitement de l'aide
            elif intent == 'help':
                if is_admin:
                    context_data['help'] = """
                    Je peux vous aider avec:
                    - Les événements à venir
                    - Les détails des profils des agents
                    - Les statistiques de présence
                    - Les informations de paiement
                    - La gestion des agents
                    
                    Exemples de questions pour un administrateur:
                    - "Quels sont les événements cette semaine?"
                    - "Montre-moi le profil de l'agent 123"
                    - "Quelles sont les statistiques de présence de l'agent 456?"
                    - "Liste tous les agents"
                    - "Résumé des présences de tous les agents"
                    """
                else:
                    context_data['help'] = """
                    Je peux vous aider avec:
                    - Vos événements à venir
                    - Les détails de votre profil
                    - Vos statistiques de présence
                    - Vos informations de paiement
                    
                    Exemples de questions:
                    - "Quels sont mes événements cette semaine?"
                    - "Quel est mon prochain événement?"
                    - "Y a-t-il des événements à Paris?"
                    - "Montre-moi mon profil"
                    - "Quelles sont mes statistiques de présence?"
                    - "Quand sera mon prochain paiement?"
                    """
            
            # Informations générales sur l'utilisateur (toujours incluses)
            user_info = f"""
            Informations sur l'utilisateur:
            - Nom: {user.first_name} {user.last_name}
            - Nom d'utilisateur: {user.username}
            - Rôle: {'Administrateur' if is_admin else 'Agent'}
            """
            
            # Créer le prompt avec toutes les informations contextuelles
            system_prompt = f"""
            Tu es un assistant virtuel pour une application de gestion d'agents événementiels.
            
            {user_info}
            
            """
            
            # Ajouter les données contextuelles au prompt
            for key, value in context_data.items():
                system_prompt += f"\n{value}\n"
            
            system_prompt += """
            Réponds de manière concise et professionnelle en utilisant les informations ci-dessus.
            Si on te demande des informations qui ne sont pas dans le contexte, indique que tu n'as pas 
            accès à ces informations et suggère à l'utilisateur de contacter un administrateur ou de consulter 
            l'interface de l'application.
            """
            
            # Appeler l'API Gemini
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            response = model.generate_content([
                system_prompt,
                user_message
            ])
            
            # Retourner la réponse avec l'action si nécessaire
            return Response({
                "response": response.text,
                "success": True,
                "intent": intent,
                "action": action_required,
                "action_data": action_data
            })
            
        except Exception as e:
            logger.error(f"Erreur chatbot: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": "Une erreur s'est produite lors de la communication avec l'assistant"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )