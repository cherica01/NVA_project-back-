
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Notification
from accounts.models import Agent
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from .serializers import NotificationSerializer
from .models import Payment
from django.db import models
from .serializers import PaymentSerializer
from django.shortcuts import get_object_or_404
from .serializers import EventSerializer
from .models import Event
from rest_framework.permissions import IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
#POST
class SendNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Vérifie si l'utilisateur est un administrateur
        if not request.user.is_superuser:
            return Response(
                {"detail": "Permission denied. Only administrators can send notifications."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Récupère les données de la requête
        message = request.data.get('message')
        date = request.data.get('date')
        recipient_ids = request.data.get('recipient_ids')  # Liste des IDs des agents

        # Vérifie les champs obligatoires
        if not message or not date or not recipient_ids:
            return Response(
                {"detail": "Missing required fields: message, date, recipient_ids."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Récupère les agents correspondants aux IDs fournis
        try:
            recipients = Agent.objects.filter(id__in=recipient_ids)
            if not recipients.exists():
                raise Agent.DoesNotExist
        except Agent.DoesNotExist:
            return Response({"detail": "One or more agents not found."}, status=status.HTTP_404_NOT_FOUND)

        # Crée des notifications pour chaque agent
        notifications = []
        for recipient in recipients:
            notification = Notification.objects.create(
                message=message,
                date=date,
                recipient=recipient,
                sender=request.user
            )
            notifications.append(notification)

        # Sérialise les notifications créées
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    
#DEMETE
class DeleteNotificationView(APIView):
    permission_classes = [IsAuthenticated]  # Assurez-vous que l'utilisateur est authentifié

    def delete(self, request, *args, **kwargs):
        # Vérifiez si l'utilisateur est un administrateur
        if not request.user.is_superuser:
            return Response({"detail": "Permission denied. Only administrators can delete notifications."},
                            status=status.HTTP_403_FORBIDDEN)

        notification_id = kwargs.get('pk')  # Récupérer l'ID de la notification à supprimer

        # Vérifier si la notification existe
        try:
            notification = Notification.objects.get(pk=notification_id)
        except Notification.DoesNotExist:
            raise NotFound({"detail": "Notification not found."})

        # Supprimer la notification
        notification.delete()

        return Response({"detail": "Notification deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

#GET    
class AgentNotificationsView(APIView):
    permission_classes = [IsAuthenticated]  # Assurez-vous que l'agent est authentifié

    def get(self, request, *args, **kwargs):
        # Filtrer les notifications pour l'agent connecté
        notifications = Notification.objects.filter(recipient=request.user)

        # Sérialiser les notifications
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AgentNotificationHistoryView(APIView):
    """
    Permet à un agent de consulter l'historique de ses notifications.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Filtrer les notifications pour l'utilisateur connecté
        notifications = Notification.objects.filter(recipient=request.user).order_by('-date')
        
        # Sérialiser les données
        serializer = NotificationSerializer(notifications, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
#GESTION DE PAYMENT 
#post

class AdminPaymentView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        data = request.data
        try:
            agent = Agent.objects.get(id=data['agent_id'])

            # Créer un enregistrement de paiement
            payment = Payment.objects.create(
                agent=agent,
                work_days=int(data.get('work_days', 0)),
                amount=float(data.get('amount', 0.0)),
            )

            # Mettre à jour le total des paiements pour l'agent
            agent.total_payments += payment.total_payment
            agent.save()

            return Response(
                {
                    "message": "Paiement effectué avec succès",
                    "username": agent.username,
                    "total_payment": payment.total_payment,
                },
                status=status.HTTP_201_CREATED,
            )
        except Agent.DoesNotExist:
            return Response(
                {"error": "Agent introuvable"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError:
            return Response(
                {"error": "Les champs 'work_days' et 'amount' doivent être des nombres."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

#GET
    
class AgentTotalPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            agent = request.user
            return Response(
                {
                    "username": agent.username,
                    "total_payments": agent.total_payments,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
class PaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(agent=request.user).order_by('-payment_date')
        serializer = PaymentSerializer(payments, many=True)
        return Response(
            {
                "username": request.user.username,
                "total_payments": request.user.total_payments,
                "payment_history": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
#gestion event 

#(post)

class CreateEventView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()
            # Inclure les usernames des agents
            agents_usernames = [agent.username for agent in event.agents.all()]
            return Response({
                "message": "Event created successfully!",
                "event": {
                    "location": event.location,
                    "company_name": event.company_name,
                    "event_code": event.event_code,
                    "start_date": event.start_date,
                    "end_date": event.end_date,
                    "agents": agents_usernames
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#patch
class UpdateEventView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event, data=request.data)
        if serializer.is_valid():
            updated_event = serializer.save()
            # Inclure les usernames des agents
            agents_usernames = [agent.username for agent in updated_event.agents.all()]
            return Response({
                "message": "Event updated successfully!",
                "event": {
                    "location": updated_event.location,
                    "company_name": updated_event.company_name,
                    "event_code": updated_event.event_code,
                    "start_date": updated_event.start_date,
                    "end_date": updated_event.end_date,
                    "agents": agents_usernames
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #delete
    
class DeleteEventView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
            event.delete()
            return Response(
                {"message": "Event deleted successfully!"},
                status=status.HTTP_204_NO_CONTENT
            )
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )
class ListEventsView(ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
   # permission_classes = [IsAuthenticated]

    # Ajout des options de filtrage, recherche et tri
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['start_date', 'end_date', 'location', 'company_name']  # Champs pour filtrer
    search_fields = ['location', 'company_name', 'event_code']  # Champs pour rechercher
    ordering_fields = ['start_date', 'end_date', 'location']  # Champs pour trier
    ordering = ['start_date']  # Tri par défaut