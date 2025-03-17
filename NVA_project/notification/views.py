from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import NotificationSerializer, NotificationCreateSerializer

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Liste toutes les notifications.
        Pour les admins: toutes les notifications
        Pour les agents: uniquement leurs notifications
        """
        if hasattr(request.user, 'is_staff') and request.user.is_staff:
            notifications = Notification.objects.all()
        else:
            notifications = Notification.objects.filter(recipient=request.user)
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class NotificationDetailView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Récupère les détails d'une notification spécifique.
        """
        notification = get_object_or_404(Notification, pk=pk)
        
        # Vérifier que l'utilisateur est autorisé à voir cette notification
        if not request.user.is_staff and request.user != notification.recipient:
            return Response({"error": "Vous n'êtes pas autorisé à voir cette notification."}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        """
        Supprime une notification.
        """
        notification = get_object_or_404(Notification, pk=pk)
        
        # Vérifier que l'utilisateur est autorisé à supprimer cette notification
        if not request.user.is_staff and request.user != notification.recipient:
            return Response({"error": "Vous n'êtes pas autorisé à supprimer cette notification."}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SendNotificationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Envoie une notification à un agent.
        Réservé aux admins.
        """
        # Vérifier que l'utilisateur est un admin
        if not hasattr(request.user, 'is_staff') or not request.user.is_staff:
            return Response({"error": "Seuls les administrateurs peuvent envoyer des notifications."}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        serializer = NotificationCreateSerializer(data=request.data)
        if serializer.is_valid():
            notification = serializer.save()
            return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MarkNotificationAsReadView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def post(self, request, notification_id):
        """
        Marque une notification comme lue.
        """
        try:
            # Pour les agents, ne permettre de marquer que leurs propres notifications
            if hasattr(request.user, 'is_staff') and request.user.is_staff:
                notification = Notification.objects.get(id=notification_id)
            else:
                notification = Notification.objects.get(id=notification_id, recipient=request.user)
        except Notification.DoesNotExist:
            return Response({"error": "Notification non trouvée."}, status=status.HTTP_404_NOT_FOUND)
        
        notification.is_read = True
        notification.save()
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

class AgentNotificationsView(APIView):
    #permission_classes = [IsAuthenticated]
    def get(self, request):
        """
        Récupère toutes les notifications de l'agent authentifié.
        """
        notifications = Notification.objects.filter(recipient=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class UnreadNotificationsCountView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Récupère le nombre de notifications non lues pour l'agent authentifié.
        """
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({"unread_count": count})