from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.db.models import Q
from .models import Presence, PresencePhoto
from .serializers import (
    PresenceSerializer, PresenceDetailSerializer, PresenceCreateSerializer, 
    PresencePhotoUploadSerializer, PresenceStatusUpdateSerializer
)

class PresenceListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Liste toutes les présences.
        """
        presences = Presence.objects.all()
        serializer = PresenceSerializer(presences, many=True)
        return Response(serializer.data)

class PresenceDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Récupère les détails d'une présence spécifique.
        """
        presence = get_object_or_404(Presence, pk=pk)
        serializer = PresenceDetailSerializer(presence)
        return Response(serializer.data)

class CreatePresenceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Crée une nouvelle présence.
        """
        serializer = PresenceCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            presence = serializer.save()
            return Response(PresenceSerializer(presence).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UploadPresencePhotoView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    
    def post(self, request, presence_id):
        """
        Télécharge une photo pour une présence spécifique.
        """
        try:
            presence = Presence.objects.get(id=presence_id)
        except Presence.DoesNotExist:
            return Response({"error": "Présence non trouvée."}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier que l'utilisateur est bien l'agent associé à cette présence
        if request.user != presence.agent:
            return Response({"error": "Vous n'êtes pas autorisé à ajouter des photos à cette présence."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PresencePhotoUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(presence=presence)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdatePresenceStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, presence_id):
        """
        Met à jour le statut d'une présence (approuver/rejeter).
        """
        presence = get_object_or_404(Presence, id=presence_id)
        serializer = PresenceStatusUpdateSerializer(presence, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(PresenceSerializer(presence).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.db.models import Q
import datetime
import calendar
from django.utils import timezone
class PresenceDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Récupère des statistiques sur les présences pour le mois spécifié.
        """
        month_str = request.query_params.get('month', None)
        
        # Déterminer la plage de dates
        if month_str:
            try:
                year, month = map(int, month_str.split('-'))
                month_date = datetime.date(year, month, 1)
                _, days_in_month = calendar.monthrange(year, month)
                month_end = datetime.date(year, month, days_in_month)
                print(f"Date range: {month_date} to {month_end}")
            except (ValueError, TypeError):
                return Response({"error": "Format de mois invalide. Utilisez YYYY-MM"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            today = timezone.now().date()
            month_date = datetime.date(today.year, today.month, 1)
            _, days_in_month = calendar.monthrange(today.year, today.month)
            month_end = datetime.date(today.year, today.month, days_in_month)
        
        # Filtrer les présences pour le mois donné
        query = Q(timestamp__date__gte=month_date, timestamp__date__lte=month_end)
        
        # Statistiques sur les présences globales
        total_presences = Presence.objects.filter(query).count()
        approved_presences = Presence.objects.filter(query & Q(status='approved')).count()
        rejected_presences = Presence.objects.filter(query & Q(status='rejected')).count()
        pending_presences = Presence.objects.filter(query & Q(status='pending')).count()

        # Statistiques par agent
        agent_stats = Presence.objects.filter(query).values('agent__username').annotate(
            total=Count('id'),
            approved=Count('id', filter=Q(status='approved')),
            rejected=Count('id', filter=Q(status='rejected')),
            pending=Count('id', filter=Q(status='pending'))
        )

        print("Agent stats:", agent_stats)

        return Response({
            'total_presences': total_presences,
            'approved_presences': approved_presences,
            'rejected_presences': rejected_presences,
            'pending_presences': pending_presences,
            'agent_stats': agent_stats
        })


class AgentPresencesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Récupère toutes les présences de l'agent authentifié.
        """
        presences = Presence.objects.filter(agent=request.user)
        serializer = PresenceSerializer(presences, many=True)
        return Response(serializer.data)