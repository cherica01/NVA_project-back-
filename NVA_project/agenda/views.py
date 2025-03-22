from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
import calendar
import datetime
from event.models import Event
from .models import AgentAvailability, AgentPreference
from .serializers import (
    EventForAgendaSerializer, 
    AgentAvailabilitySerializer, 
    AgentPreferenceSerializer,
    AgendaMonthSerializer
)

class AgentEventsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Récupère tous les événements auxquels l'agent est assigné.
        """
        events = Event.objects.filter(agents=request.user).order_by('start_date')
        serializer = EventForAgendaSerializer(events, many=True)
        return Response(serializer.data)

class AgentMonthlyEventsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, year, month):
        """
        Récupère les événements de l'agent pour un mois spécifique.
        """
        try:
            year = int(year)
            month = int(month)
            if month < 1 or month > 12:
                return Response(
                    {"error": "Le mois doit être compris entre 1 et 12."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {"error": "L'année et le mois doivent être des nombres entiers."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Déterminer le premier et le dernier jour du mois
        first_day = datetime.date(year, month, 1)
        last_day = datetime.date(year, month, calendar.monthrange(year, month)[1])
        
        # Récupérer les événements pour ce mois
        events = Event.objects.filter(
            agents=request.user,
            start_date__lte=last_day,
            end_date__gte=first_day
        ).order_by('start_date')
        
        # Récupérer les disponibilités pour ce mois
        availabilities = AgentAvailability.objects.filter(
            agent=request.user,
            date__gte=first_day,
            date__lte=last_day
        )
        
        # Créer un dictionnaire pour chaque jour du mois
        days = []
        for day in range(1, calendar.monthrange(year, month)[1] + 1):
            current_date = datetime.date(year, month, day)
            
            # Événements pour ce jour
            day_events = [
                {
                    'id': event.id,
                    'title': f"{event.company_name} - {event.event_code}",
                    'location': event.location,
                    'start_date': event.start_date,
                    'end_date': event.end_date
                }
                for event in events
                if (event.start_date.date() <= current_date <= event.end_date.date())
            ]
            
            # Disponibilité pour ce jour
            availability = availabilities.filter(date=current_date).first()
            is_available = availability.is_available if availability else True
            note = availability.note if availability else None
            
            days.append({
                'date': current_date.isoformat(),
                'day': day,
                'events': day_events,
                'is_available': is_available,
                'note': note,
                'is_weekend': current_date.weekday() >= 5,  # 5 = Samedi, 6 = Dimanche
                'is_today': current_date == timezone.now().date()
            })
        
        data = {
            'year': year,
            'month': month,
            'days': days
        }
        
        serializer = AgendaMonthSerializer(data)
        return Response(serializer.data)

class AgentAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Récupère toutes les disponibilités de l'agent.
        """
        availabilities = AgentAvailability.objects.filter(agent=request.user).order_by('date')
        serializer = AgentAvailabilitySerializer(availabilities, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """
        Crée ou met à jour une disponibilité pour l'agent.
        """
        serializer = AgentAvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            # Vérifier si une disponibilité existe déjà pour cette date
            date = serializer.validated_data['date']
            availability, created = AgentAvailability.objects.get_or_create(
                agent=request.user,
                date=date,
                defaults={
                    'is_available': serializer.validated_data['is_available'],
                    'note': serializer.validated_data.get('note')
                }
            )
            
            if not created:
                # Mettre à jour la disponibilité existante
                availability.is_available = serializer.validated_data['is_available']
                availability.note = serializer.validated_data.get('note')
                availability.save()
            
            return Response(
                AgentAvailabilitySerializer(availability).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AgentAvailabilityDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Récupère une disponibilité spécifique de l'agent.
        """
        availability = get_object_or_404(AgentAvailability, pk=pk, agent=request.user)
        serializer = AgentAvailabilitySerializer(availability)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """
        Met à jour une disponibilité spécifique de l'agent.
        """
        availability = get_object_or_404(AgentAvailability, pk=pk, agent=request.user)
        serializer = AgentAvailabilitySerializer(availability, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Supprime une disponibilité spécifique de l'agent.
        """
        availability = get_object_or_404(AgentAvailability, pk=pk, agent=request.user)
        availability.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AgentPreferenceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Récupère les préférences de l'agent.
        """
        preference, created = AgentPreference.objects.get_or_create(agent=request.user)
        serializer = AgentPreferenceSerializer(preference)
        return Response(serializer.data)
    
    def put(self, request):
        """
        Met à jour les préférences de l'agent.
        """
        preference, created = AgentPreference.objects.get_or_create(agent=request.user)
        serializer = AgentPreferenceSerializer(preference, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)