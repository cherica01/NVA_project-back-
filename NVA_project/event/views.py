from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Event
from accounts.models import Agent
from .serializers import EventSerializer, EventDetailSerializer, EventCreateSerializer, AgentEventSerializer
from datetime import datetime

class EventListView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Liste tous les événements.
        """
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

class EventDetailView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Récupère les détails d'un événement spécifique.
        """
        event = get_object_or_404(Event, pk=pk)
        serializer = EventDetailSerializer(event)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """
        Met à jour un événement existant.
        """
        event = get_object_or_404(Event, pk=pk)
        serializer = EventCreateSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Supprime un événement.
        """
        event = get_object_or_404(Event, pk=pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CreateEventView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Crée un nouvel événement.
        """
        serializer = EventCreateSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()
            return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AvailableAgentsView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Récupère les agents disponibles pour une période donnée.
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({"error": "Les dates de début et de fin sont requises."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return Response({"error": "Format de date invalide. Utilisez YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Trouver les agents qui ne sont pas déjà assignés à un événement pendant cette période
        busy_agents = Agent.objects.filter(
            events__start_date__lte=end_date,
            events__end_date__gte=start_date
        ).distinct()
        
        available_agents = Agent.objects.exclude(id__in=busy_agents.values_list('id', flat=True))
        
        # Utiliser le sérialiseur d'agent pour renvoyer les données
        from accounts.serializers import AgentSerializer
        serializer = AgentSerializer(available_agents, many=True)
        return Response(serializer.data)

class AgentEventsView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Récupère tous les événements auxquels l'agent est assigné.
        """
        # Supposons que l'agent est l'utilisateur authentifié
        agent = request.user
        
        # Récupérer tous les événements auxquels l'agent est assigné
        events = Event.objects.filter(agents=agent)
        
        serializer = AgentEventSerializer(events, many=True)
        return Response(serializer.data)

class UpdateEventView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        """
        Met à jour un événement existant.
        """
        event = get_object_or_404(Event, pk=pk)
        serializer = EventCreateSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteEventView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        """
        Supprime un événement.
        """
        event = get_object_or_404(Event, pk=pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)